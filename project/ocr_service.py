import os
import logging
from typing import List, Dict, Any, Optional
from PIL import Image
import numpy as np
from paddleocr import PaddleOCR
import io

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    """PaddleOCR을 사용한 한글 텍스트 인식 서비스"""
    
    def __init__(self, use_gpu: bool = False):
        """
        OCR 서비스 초기화
        
        Args:
            use_gpu (bool): GPU 사용 여부 (기본값: False) - 현재 버전에서는 무시됨
        """
        try:
            logger.info("PaddleOCR 모델 로딩 중...")
            self.ocr = PaddleOCR(
                lang='korean'  # 한국어 모델
            )
            logger.info("PaddleOCR 모델 로딩 완료")
        except Exception as e:
            logger.error(f"PaddleOCR 초기화 실패: {e}")
            raise
    
    def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        이미지에서 텍스트 추출
        
        Args:
            image_path (str): 이미지 파일 경로
            
        Returns:
            Dict[str, Any]: 추출된 텍스트 정보
        """
        try:
            logger.info(f"이미지 처리 시작: {image_path}")
            
            # 이미지 파일 존재 확인
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            
            # OCR 실행
            result = self.ocr.ocr(image_path)
            
            if not result or not result[0]:
                logger.warning("텍스트를 찾을 수 없습니다")
                return {
                    "success": True,
                    "text": "",
                    "words": [],
                    "message": "이미지에서 텍스트를 찾을 수 없습니다"
                }
            
            # 결과 파싱
            words = []
            full_text = ""
            
            for line in result[0]:
                if line:
                    # PaddleOCR 3.1.0 결과 구조: [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence)]
                    bbox = line[0]  # 바운딩 박스 좌표
                    text_info = line[1]  # (텍스트, 신뢰도)
                    
                    if text_info:
                        text = text_info[0]
                        confidence = float(text_info[1])
                        
                        word_info = {
                            "text": text,
                            "confidence": confidence,
                            "bbox": bbox
                        }
                        words.append(word_info)
                        full_text += text + " "
            
            # 결과 정리
            full_text = full_text.strip()
            
            logger.info(f"텍스트 추출 완료: {len(words)}개 단어, 총 {len(full_text)}자")
            
            return {
                "success": True,
                "text": full_text,
                "words": words,
                "word_count": len(words),
                "character_count": len(full_text),
                "message": "텍스트 추출이 완료되었습니다"
            }
            
        except Exception as e:
            logger.error(f"텍스트 추출 중 오류 발생: {e}")
            return {
                "success": False,
                "text": "",
                "words": [],
                "error": str(e),
                "message": "텍스트 추출 중 오류가 발생했습니다"
            }
    
    def extract_text_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        바이트 데이터에서 텍스트 추출
        
        Args:
            image_bytes (bytes): 이미지 바이트 데이터
            
        Returns:
            Dict[str, Any]: 추출된 텍스트 정보
        """
        try:
            logger.info("바이트 데이터에서 텍스트 추출 시작")
            
            # 바이트 데이터를 PIL Image로 변환
            image = Image.open(io.BytesIO(image_bytes))
            
            # OCR 실행
            result = self.ocr.ocr(np.array(image))
            
            if not result or not result[0]:
                logger.warning("텍스트를 찾을 수 없습니다")
                return {
                    "success": True,
                    "text": "",
                    "words": [],
                    "message": "이미지에서 텍스트를 찾을 수 없습니다"
                }
            
            # 결과 파싱
            words = []
            full_text = ""
            
            for line in result[0]:
                if line:
                    bbox = line[0]
                    text_info = line[1]
                    
                    if text_info:
                        text = text_info[0]
                        confidence = float(text_info[1])
                        
                        word_info = {
                            "text": text,
                            "confidence": confidence,
                            "bbox": bbox
                        }
                        words.append(word_info)
                        full_text += text + " "
            
            full_text = full_text.strip()
            
            logger.info(f"텍스트 추출 완료: {len(words)}개 단어, 총 {len(full_text)}자")
            
            return {
                "success": True,
                "text": full_text,
                "words": words,
                "word_count": len(words),
                "character_count": len(full_text),
                "message": "텍스트 추출이 완료되었습니다"
            }
            
        except Exception as e:
            logger.error(f"텍스트 추출 중 오류 발생: {e}")
            return {
                "success": False,
                "text": "",
                "words": [],
                "error": str(e),
                "message": "텍스트 추출 중 오류가 발생했습니다"
            } 