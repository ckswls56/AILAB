#!/usr/bin/env python3
"""
LCEL 실습 테스트 스크립트
"""

import json
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# API 키 확인
if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
    print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
    print("📝 .env 파일에 실제 OpenAI API 키를 설정한 후 다시 시도해주세요.")
    exit(1)

from lcel_practice import create_basic_chain, create_json_chain, create_sequential_chain

def test_basic_chain():
    """기본 체인 테스트"""
    print("🧪 기본 체인 테스트 중...")
    
    chain = create_basic_chain()
    
    test_text = "오늘은 정말 좋은 날씨였다. 친구들과 함께 공원에서 피크닉을 했다."
    
    try:
        result = chain.invoke({"text": test_text})
        print("✅ 기본 체인 테스트 성공!")
        print(f"   요약: {result['summary']}")
        print(f"   감정: {result['sentiment']}")
        return True
    except Exception as e:
        print(f"❌ 기본 체인 테스트 실패: {e}")
        return False

def test_json_chain():
    """JSON 체인 테스트"""
    print("\n🧪 JSON 체인 테스트 중...")
    
    chain = create_json_chain()
    
    test_text = "오늘 시험에서 떨어졌다. 열심히 공부했는데도 결과가 좋지 않아서 정말 속상하다."
    
    try:
        result = chain.invoke({"text": test_text})
        print("✅ JSON 체인 테스트 성공!")
        print("   구조화된 결과:")
        print(json.dumps(result, ensure_ascii=False, indent=4))
        return True
    except Exception as e:
        print(f"❌ JSON 체인 테스트 실패: {e}")
        return False

def test_sequential_chain():
    """순차적 체인 테스트"""
    print("\n🧪 순차적 체인 테스트 중...")
    
    chain = create_sequential_chain()
    
    test_text = "오늘은 평범한 하루였다. 아침에 일어나서 출근하고, 저녁에 집에 와서 TV를 봤다."
    
    try:
        result = chain.invoke({"text": test_text})
        print("✅ 순차적 체인 테스트 성공!")
        print(f"   감정 분석 결과: {result}")
        return True
    except Exception as e:
        print(f"❌ 순차적 체인 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 LCEL 실습 테스트를 시작합니다...\n")
    
    tests = [
        test_basic_chain,
        test_json_chain,
        test_sequential_chain
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print("⚠️  일부 테스트가 실패했습니다.")

if __name__ == "__main__":
    main() 