import os
import uuid
import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("OCR 패키지가 설치되지 않았습니다. 스캔된 PDF 처리가 제한됩니다.")

from models import DocumentInfo
from llm_client import InternalLLMClient

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF 문서 처리 및 벡터화 서비스"""
    
    def __init__(self):
        self.llm_client = InternalLLMClient()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # OCR 설정
        if OCR_AVAILABLE:
            # pytesseract 설정
            self.ocr_config = r'--oem 3 --psm 6'
            
            # 사용 가능한 언어 확인 후 설정
            try:
                import pytesseract
                available_langs = pytesseract.get_languages()
                logger.info(f"사용 가능한 OCR 언어: {available_langs}")
                
                # 한국어 지원 확인 후 설정
                if 'kor' in available_langs and 'eng' in available_langs:
                    self.ocr_lang = 'kor+eng'  # 한국어+영어
                    logger.info("OCR 언어: 한국어+영어 지원 ✅")
                elif 'eng' in available_langs:
                    self.ocr_lang = 'eng'  # 영어만
                    logger.info("OCR 언어: 영어만 지원")
                else:
                    self.ocr_lang = 'eng'  # 기본값
                    logger.warning("OCR 언어: 기본 영어 설정 (언어 확인 실패)")
            except Exception as e:
                self.ocr_lang = 'eng'  # fallback
                logger.warning(f"OCR 언어 설정 실패, 영어로 fallback: {e}")
    
    def _extract_text_with_ocr(self, file_path: str) -> str:
        """OCR을 사용하여 PDF에서 텍스트 추출"""
        if not OCR_AVAILABLE:
            logger.error("OCR 패키지가 설치되지 않았습니다.")
            raise RuntimeError("OCR 패키지가 설치되지 않았습니다.")
        
        try:
            logger.info(f"OCR로 PDF 처리 시작: {file_path}")
            
            # 파일 존재 확인
            if not os.path.exists(file_path):
                logger.error(f"PDF 파일이 존재하지 않음: {file_path}")
                raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {file_path}")
            
            # 테서랙트 버전 확인
            try:
                version = pytesseract.get_tesseract_version()
                logger.info(f"Tesseract 버전: {version}")
            except Exception as e:
                logger.error(f"Tesseract 접근 실패: {e}")
                raise RuntimeError(f"Tesseract가 설치되지 않았거나 접근할 수 없습니다: {e}")
            
            # PDF를 이미지로 변환
            logger.info("PDF를 이미지로 변환 시작...")
            try:
                images = convert_from_path(file_path, dpi=300)
                logger.info(f"PDF를 {len(images)}개 이미지로 변환 완료")
            except Exception as e:
                logger.error(f"PDF→이미지 변환 실패: {e}")
                raise RuntimeError(f"PDF를 이미지로 변환할 수 없습니다. poppler-utils가 설치되었는지 확인하세요: {e}")
            
            # 각 페이지에서 OCR로 텍스트 추출
            extracted_texts = []
            total_pages = len(images)
            logger.info(f"총 {total_pages}개 페이지에서 OCR 시작")
            
            for i, image in enumerate(images):
                try:
                    logger.info(f"페이지 {i+1}/{total_pages} OCR 처리 중...")
                    
                    # 이미지 정보 확인
                    logger.debug(f"페이지 {i+1} 이미지 크기: {image.size}")
                    
                    # OCR 수행
                    logger.debug(f"OCR 설정 - 언어: {self.ocr_lang}, 설정: {self.ocr_config}")
                    text = pytesseract.image_to_string(
                        image, 
                        lang=self.ocr_lang,
                        config=self.ocr_config
                    )
                    
                    if text and text.strip():
                        extracted_texts.append(text.strip())
                        logger.info(f"페이지 {i+1}: {len(text.strip())}자 추출 성공")
                    else:
                        logger.warning(f"페이지 {i+1}: OCR 결과가 비어있음")
                        
                except Exception as e:
                    logger.error(f"페이지 {i+1} OCR 처리 실패: {type(e).__name__}: {e}")
                    continue
            
            combined_text = "\n\n".join(extracted_texts)
            logger.info(f"OCR 완료: 총 {len(combined_text)}자 추출")
            
            return combined_text
            
        except Exception as e:
            logger.error(f"OCR 처리 중 오류: {e}")
            raise
    
    async def process_pdf(self, file_path: str, filename: str, db: AsyncSession) -> Dict[str, Any]:
        """PDF 파일을 처리하고 벡터화하여 데이터베이스에 저장"""
        try:
            # Step 1: 일반적인 PDF 텍스트 추출 시도
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            # 전체 문서 내용 결합
            full_content = "\n".join([page.page_content for page in pages])
            
            logger.info(f"PDF '{filename}': {len(pages)}개 페이지, 일반 추출로 {len(full_content)}자 획득")
            
            # Step 2: 기본 텍스트 검증 (비어있어도 OCR 시도 가능하면 계속 진행)
            if not full_content or len(full_content.strip()) == 0:
                logger.warning(f"PDF '{filename}': 기본 텍스트 추출 실패 (빈 내용)")
                if not OCR_AVAILABLE:
                    error_msg = "PDF에서 텍스트를 추출할 수 없습니다 (OCR 기능이 비활성화됨)"
                    raise ValueError(error_msg)
                else:
                    logger.info(f"PDF '{filename}': OCR로 텍스트 추출 시도...")
                    # 빈 텍스트로 시작하지만 OCR에서 텍스트를 얻을 수 있음
                    full_content = ""
            
            # Step 3: 첫 번째 청크 생성 시도
            original_content = full_content
            texts = self.text_splitter.split_text(full_content)
            valid_texts = [text.strip() for text in texts if text.strip() and len(text.strip()) > 10]
            
            logger.info(f"PDF '{filename}': 일반 추출로 {len(texts)}개 청크, {len(valid_texts)}개 유효 청크 생성")
            
            # Step 4: 청크가 부족하거나 텍스트가 부족한 경우 OCR 시도
            min_text_threshold = 500  # 500자 미만이면 OCR 시도 (기존 100자에서 증가)
            min_chunks_threshold = 3   # 3개 청크 미만이면 OCR 시도 (기존 1개에서 증가)
            use_ocr = False
            
            # 텍스트 품질 확인 (특수문자/공백 비율)
            text_content = full_content.strip()
            if text_content:
                # 알파벳, 숫자, 한글 등 의미 있는 문자 비율 계산
                meaningful_chars = sum(1 for c in text_content if c.isalnum() or c in '가-힣')
                meaningful_ratio = meaningful_chars / len(text_content) if text_content else 0
                logger.info(f"PDF '{filename}' 텍스트 품질: {meaningful_ratio:.2f} (의미있는 문자 비율)")
            else:
                meaningful_ratio = 0
            
            should_try_ocr = (
                len(text_content) == 0 or                      # 완전히 빈 텍스트 (스캔 PDF)
                len(text_content) < min_text_threshold or      # 텍스트 부족
                len(valid_texts) < min_chunks_threshold or     # 유효한 청크 부족
                meaningful_ratio < 0.7                         # 텍스트 품질 낮음 (70% 미만)
            )
            
            # 상세한 OCR 판단 로그
            logger.info(f"PDF '{filename}' OCR 필요성 판단:")
            logger.info(f"  - 텍스트 길이: {len(text_content)}자 (임계값: {min_text_threshold}자)")
            logger.info(f"  - 유효 청크: {len(valid_texts)}개 (임계값: {min_chunks_threshold}개)")
            logger.info(f"  - 텍스트 품질: {meaningful_ratio:.2f} (임계값: 0.7)")
            logger.info(f"  - OCR 시도 여부: {should_try_ocr}")
            logger.info(f"  - OCR 사용 가능: {OCR_AVAILABLE}")
            
            if should_try_ocr and OCR_AVAILABLE:
                reason = "텍스트 부족" if len(full_content.strip()) < min_text_threshold else "유효 청크 부족"
                logger.info(f"PDF '{filename}': {reason}({len(full_content.strip())}자, {len(valid_texts)}개 청크), OCR 시도...")
                
                try:
                    ocr_content = self._extract_text_with_ocr(file_path)
                    if len(ocr_content.strip()) > 0:
                        # OCR 결과로 청크 재생성
                        ocr_texts = self.text_splitter.split_text(ocr_content)
                        ocr_valid_texts = [text.strip() for text in ocr_texts if text.strip() and len(text.strip()) > 10]
                        
                        logger.info(f"PDF '{filename}': OCR로 {len(ocr_texts)}개 청크, {len(ocr_valid_texts)}개 유효 청크 생성")
                        
                        # OCR 결과가 더 좋으면 사용
                        if (len(ocr_valid_texts) > len(valid_texts) or 
                            (len(ocr_valid_texts) >= len(valid_texts) and len(ocr_content.strip()) > len(full_content.strip()))):
                            full_content = ocr_content
                            texts = ocr_texts
                            valid_texts = ocr_valid_texts
                            use_ocr = True
                            logger.info(f"PDF '{filename}': OCR 결과 채택 ({len(ocr_content)}자, {len(ocr_valid_texts)}개 유효 청크)")
                        else:
                            logger.info(f"PDF '{filename}': 기존 결과가 더 좋음, OCR 결과 무시")
                    else:
                        logger.warning(f"PDF '{filename}': OCR 결과가 비어있음")
                        
                except Exception as ocr_error:
                    logger.error(f"PDF '{filename}': OCR 실패 - {ocr_error}")
            elif should_try_ocr and not OCR_AVAILABLE:
                logger.warning(f"PDF '{filename}': OCR이 필요하지만 패키지가 설치되지 않음")
            elif not should_try_ocr:
                logger.info(f"PDF '{filename}': OCR 불필요 (조건 만족)")
            
            # Step 5: 최종 검증 (OCR 결과 포함)
            content_length = len(full_content.strip())
            
            # 최종 결과 검증
            if len(valid_texts) == 0:
                error_msg = f"유효한 텍스트 청크를 생성할 수 없습니다. (총 텍스트: {content_length}자)"
                
                if use_ocr:
                    error_msg += " OCR을 시도했지만 유효한 청크를 생성하지 못했습니다."
                elif should_try_ocr and OCR_AVAILABLE:
                    error_msg += " OCR 시도 중 오류가 발생했습니다."
                elif not OCR_AVAILABLE:
                    error_msg += " OCR 기능이 비활성화되어 있어 스캔된 PDF를 처리할 수 없습니다."
                else:
                    error_msg += " 텍스트 추출은 성공했지만 의미있는 청크를 생성하지 못했습니다."
                    
                raise ValueError(error_msg)
            
            # 최소 텍스트 길이 검증 (OCR 성공한 경우는 더 관대하게)
            min_final_length = 5 if use_ocr else 10
            if content_length < min_final_length:
                raise ValueError(f"추출된 텍스트가 너무 짧습니다 ({content_length}자, 최소 {min_final_length}자 필요)")
            
            # 문서 ID 생성
            document_id = str(uuid.uuid4())
            
            # 문서 정보를 데이터베이스에 저장
            await db.execute(
                text("""
                    INSERT INTO documents (id, filename, content, metadata)
                    VALUES (:id, :filename, :content, :metadata)
                """),
                {
                    "id": document_id,
                    "filename": filename,
                    "content": full_content,
                    "metadata": json.dumps({
                        "page_count": len(pages),
                        "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                        "extraction_method": "OCR" if use_ocr else "Standard",
                        "ocr_available": OCR_AVAILABLE,
                        "content_length": content_length,
                        "total_chunks": len(texts),
                        "valid_chunks": len(valid_texts),
                        "original_content_length": len(original_content.strip())
                    })
                }
            )
            
            # 유효한 청크만 사용
            texts = valid_texts
            
            # 각 청크를 벡터화하고 저장
            for i, chunk_text in enumerate(texts):
                # 임베딩 생성 (로컬 CPU에서 처리)
                embedding = self.llm_client.get_embedding(chunk_text)
                
                # 청크를 데이터베이스에 저장
                await db.execute(
                    text("""
                        INSERT INTO document_chunks (document_id, chunk_index, content, embedding, metadata)
                        VALUES (:document_id, :chunk_index, :content, :embedding, :metadata)
                    """),
                    {
                        "document_id": document_id,
                        "chunk_index": i,
                        "content": chunk_text,
                        "embedding": f"[{','.join(map(str, embedding))}]",  # PostgreSQL vector 형식으로 변환
                        "metadata": json.dumps({
                            "chunk_length": len(chunk_text),
                            "page_numbers": self._extract_page_numbers(chunk_text, pages)
                        })
                    }
                )
            
            await db.commit()
            
            extraction_info = f"{'OCR' if use_ocr else '일반'} 추출"
            logger.info(f"PDF '{filename}' 처리 완료: {len(texts)}개 유효 청크 생성 ({extraction_info}, {content_length}자)")
            
            return {
                "document_id": document_id,
                "chunks_count": len(texts),
                "extraction_method": "OCR" if use_ocr else "Standard",
                "content_length": content_length,
                "original_content_length": len(original_content.strip())
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"PDF 처리 중 오류 발생: {e}")
            raise
    
    def _extract_page_numbers(self, chunk_text: str, pages: List) -> List[int]:
        """청크가 포함된 페이지 번호 추출 (간단한 구현)"""
        # 실제로는 더 정교한 페이지 매핑이 필요할 수 있습니다
        page_numbers = []
        for i, page in enumerate(pages):
            if chunk_text[:100] in page.page_content:
                page_numbers.append(i + 1)
                break
        return page_numbers or [1]
    
    async def get_documents_list(self, db: AsyncSession) -> List[DocumentInfo]:
        """저장된 문서 목록 조회"""
        try:
            result = await db.execute(
                text("""
                    SELECT 
                        d.id,
                        d.filename,
                        LEFT(d.content, 200) as content_preview,
                        COUNT(dc.id) as chunks_count,
                        d.created_at
                    FROM documents d
                    LEFT JOIN document_chunks dc ON d.id = dc.document_id
                    GROUP BY d.id, d.filename, d.content, d.created_at
                    ORDER BY d.created_at DESC
                """)
            )
            
            documents = []
            for row in result:
                documents.append(DocumentInfo(
                    id=str(row.id),
                    filename=row.filename,
                    content_preview=row.content_preview,
                    chunks_count=row.chunks_count,
                    created_at=row.created_at
                ))
            
            return documents
            
        except Exception as e:
            logger.error(f"문서 목록 조회 중 오류 발생: {e}")
            raise
    
    async def delete_document(self, document_id: str, db: AsyncSession) -> bool:
        """문서 삭제"""
        try:
            # 문서 존재 확인
            result = await db.execute(
                text("SELECT id FROM documents WHERE id = :document_id"),
                {"document_id": document_id}
            )
            
            if not result.fetchone():
                return False
            
            # 관련 청크들 먼저 삭제 (CASCADE로 자동 삭제되지만 명시적으로)
            await db.execute(
                text("DELETE FROM document_chunks WHERE document_id = :document_id"),
                {"document_id": document_id}
            )
            
            # 문서 삭제
            await db.execute(
                text("DELETE FROM documents WHERE id = :document_id"),
                {"document_id": document_id}
            )
            
            await db.commit()
            
            logger.info(f"문서 {document_id} 삭제 완료")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"문서 삭제 중 오류 발생: {e}")
            raise