#!/usr/bin/env python3
"""
PaddleOCR API 테스트 스크립트
"""

import requests
import json
import time
import os
from typing import Dict, Any

class OCRAPITester:
    """OCR API 테스트 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self) -> Dict[str, Any]:
        """헬스 체크 테스트"""
        print("🔍 헬스 체크 테스트...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            result = response.json()
            print(f"✅ 헬스 체크 성공: {result}")
            return result
        except Exception as e:
            print(f"❌ 헬스 체크 실패: {e}")
            return {"error": str(e)}
    
    def test_info(self) -> Dict[str, Any]:
        """서버 정보 테스트"""
        print("🔍 서버 정보 테스트...")
        try:
            response = self.session.get(f"{self.base_url}/info")
            result = response.json()
            print(f"✅ 서버 정보: {result}")
            return result
        except Exception as e:
            print(f"❌ 서버 정보 조회 실패: {e}")
            return {"error": str(e)}
    
    def test_ocr_upload(self, image_path: str, include_bbox: bool = False) -> Dict[str, Any]:
        """이미지 업로드 OCR 테스트"""
        print(f"🔍 이미지 업로드 OCR 테스트: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
            return {"error": "파일을 찾을 수 없습니다"}
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {'include_bbox': include_bbox}
                
                start_time = time.time()
                response = self.session.post(f"{self.base_url}/ocr/upload", files=files, data=data)
                total_time = time.time() - start_time
                
                result = response.json()
                
                if result.get("success"):
                    print(f"✅ OCR 성공!")
                    print(f"   📝 추출된 텍스트: {result.get('text', '')}")
                    print(f"   📊 단어 수: {result.get('word_count', 0)}")
                    print(f"   📏 문자 수: {result.get('character_count', 0)}")
                    print(f"   ⏱️  처리 시간: {result.get('processing_time', 0):.3f}초")
                    print(f"   🕐 총 요청 시간: {total_time:.3f}초")
                else:
                    print(f"❌ OCR 실패: {result.get('message', '')}")
                
                return result
                
        except Exception as e:
            print(f"❌ OCR 테스트 실패: {e}")
            return {"error": str(e)}
    
    def test_ocr_path(self, image_path: str, include_bbox: bool = False) -> Dict[str, Any]:
        """파일 경로 OCR 테스트"""
        print(f"🔍 파일 경로 OCR 테스트: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
            return {"error": "파일을 찾을 수 없습니다"}
        
        try:
            data = {
                'image_path': image_path,
                'include_bbox': include_bbox
            }
            
            start_time = time.time()
            response = self.session.post(f"{self.base_url}/ocr/path", data=data)
            total_time = time.time() - start_time
            
            result = response.json()
            
            if result.get("success"):
                print(f"✅ OCR 성공!")
                print(f"   📝 추출된 텍스트: {result.get('text', '')}")
                print(f"   📊 단어 수: {result.get('word_count', 0)}")
                print(f"   📏 문자 수: {result.get('character_count', 0)}")
                print(f"   ⏱️  처리 시간: {result.get('processing_time', 0):.3f}초")
                print(f"   🕐 총 요청 시간: {total_time:.3f}초")
            else:
                print(f"❌ OCR 실패: {result.get('message', '')}")
            
            return result
            
        except Exception as e:
            print(f"❌ OCR 테스트 실패: {e}")
            return {"error": str(e)}
    
    def run_all_tests(self, test_image_path: str = None):
        """모든 테스트 실행"""
        print("🚀 PaddleOCR API 테스트 시작")
        print("=" * 50)
        
        # 1. 헬스 체크
        health_result = self.test_health()
        print()
        
        # 2. 서버 정보
        info_result = self.test_info()
        print()
        
        # 3. OCR 테스트 (이미지가 제공된 경우)
        if test_image_path:
            print("📸 OCR 테스트")
            print("-" * 30)
            
            # 업로드 테스트
            upload_result = self.test_ocr_upload(test_image_path, include_bbox=True)
            print()
            
            # 경로 테스트
            path_result = self.test_ocr_path(test_image_path, include_bbox=False)
            print()
        else:
            print("⚠️  테스트 이미지가 제공되지 않아 OCR 테스트를 건너뜁니다.")
            print("   사용법: python test_api.py <이미지_경로>")
        
        print("=" * 50)
        print("🏁 테스트 완료")

def main():
    """메인 함수"""
    import sys
    
    # 명령행 인수 처리
    test_image_path = None
    if len(sys.argv) > 1:
        test_image_path = sys.argv[1]
    
    # 테스터 생성 및 실행
    tester = OCRAPITester()
    tester.run_all_tests(test_image_path)

if __name__ == "__main__":
    main() 