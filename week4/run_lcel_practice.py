#!/usr/bin/env python3
"""
LCEL 실습 실행 스크립트
"""

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 확인
api_key = os.getenv('OPENAI_API_KEY')
if not api_key or api_key == 'your_openai_api_key_here':
    print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
    print("📝 다음 단계를 따라 .env 파일을 생성하고 API 키를 설정해주세요:")
    print("   1. week4 폴더에 .env 파일을 생성하세요")
    print("   2. 다음 내용을 추가하세요:")
    print("      OPENAI_API_KEY=your_actual_openai_api_key_here")
    print("   3. your_actual_openai_api_key_here 부분을 실제 OpenAI API 키로 교체하세요")
    print("\n🔗 OpenAI API 키는 다음에서 얻을 수 있습니다: https://platform.openai.com/api-keys")
    exit(1)

# LangSmith 설정 확인 (선택사항)
langsmith_key = os.getenv('LANGCHAIN_API_KEY')
if langsmith_key:
    print("✅ LangSmith 추적이 활성화되었습니다.")
else:
    print("ℹ️  LangSmith 추적이 비활성화되었습니다. (선택사항)")

print("🚀 LCEL 실습을 시작합니다...\n")

# LCEL 실습 모듈 실행
try:
    from lcel_practice import main
    main()
except ImportError as e:
    print(f"❌ 필요한 패키지가 설치되지 않았습니다: {e}")
    print("📦 다음 명령어로 패키지를 설치해주세요:")
    print("   pip install -r requirements_lcel.txt")
except Exception as e:
    print(f"❌ 실행 중 오류가 발생했습니다: {e}") 