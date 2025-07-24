"""
LCEL 실습: 요약 및 감정 분석 체인
1. 사용자 입력을 받아 내용을 요약하기
2. 요약된 내용을 기반으로 감정 분석하기 (긍정, 부정, 중립)
3. 요약된 문장과 감정 분석 결과를 출력하기
4. JSON Output Parser로 구조화된 출력으로 변환하기
"""

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnableParallel
from pydantic import BaseModel, Field
from typing import Literal
import json

# 1. 기본 요약 및 감정 분석 체인

def create_basic_chain():
    """기본 요약 및 감정 분석 체인 생성"""
    
    # 프롬프트 템플릿 정의
    summarize_prompt = PromptTemplate.from_template(
        "다음 텍스트를 간결하게 요약해주세요. 핵심 내용만 포함하여 2-3문장으로 요약해주세요.\n\n텍스트: {text}\n\n요약:"
    )

    sentiment_prompt = PromptTemplate.from_template(
        "다음 텍스트의 감정을 분석해주세요. 다음 중 하나로 분류해주세요: 긍정, 부정, 중립\n\n텍스트: {text}\n\n감정:"
    )

    # 문자열 출력 파서
    output_parser = StrOutputParser()

    # 체인 구성
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=150)

    # 요약 체인
    summarize_chain = summarize_prompt | model | output_parser

    # 감정 분석 체인
    sentiment_chain = sentiment_prompt | model | output_parser

    # 전체 체인 - RunnableParallel을 사용하여 병렬 처리
    chain = RunnableParallel({
        "summary": summarize_chain,
        "sentiment": sentiment_chain
    })
    
    return chain

# 2. JSON Output Parser를 사용한 구조화된 출력 체인

class AnalysisResult(BaseModel):
    """분석 결과를 위한 Pydantic 모델"""
    summary: str = Field(description="텍스트 요약")
    sentiment: Literal["긍정", "부정", "중립"] = Field(description="감정 분석 결과")
    confidence: float = Field(description="감정 분석 신뢰도 (0.0-1.0)", ge=0.0, le=1.0)

def create_json_chain():
    """JSON Output Parser를 사용한 구조화된 출력 체인 생성"""
    
    # JSON 출력 파서
    json_parser = JsonOutputParser(pydantic_object=AnalysisResult)
    
    # 구조화된 프롬프트 템플릿
    structured_prompt = PromptTemplate.from_template(
        """다음 텍스트를 분석하여 JSON 형식으로 결과를 출력해주세요.

텍스트: {text}

다음 JSON 형식으로 응답해주세요:
{{
    "summary": "텍스트의 핵심 내용을 2-3문장으로 요약",
    "sentiment": "긍정, 부정, 중립 중 하나",
    "confidence": 0.0-1.0 사이의 감정 분석 신뢰도
}}

응답:"""
    )
    
    # 체인 구성
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=200)
    
    # 구조화된 체인
    structured_chain = structured_prompt | model | json_parser
    
    return structured_chain

# 3. 순차적 처리 체인 (요약 -> 감정 분석)

def create_sequential_chain():
    """순차적 처리 체인 생성 (요약 후 감정 분석)"""
    
    # 요약 프롬프트
    summarize_prompt = PromptTemplate.from_template(
        "다음 텍스트를 간결하게 요약해주세요. 핵심 내용만 포함하여 2-3문장으로 요약해주세요.\n\n텍스트: {text}\n\n요약:"
    )
    
    # 감정 분석 프롬프트 (요약된 텍스트를 입력으로 받음)
    sentiment_prompt = PromptTemplate.from_template(
        "다음 요약된 텍스트의 감정을 분석해주세요. 다음 중 하나로 분류해주세요: 긍정, 부정, 중립\n\n요약: {summary}\n\n감정:"
    )
    
    # 출력 파서
    output_parser = StrOutputParser()
    
    # 체인 구성
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, max_tokens=150)
    
    # 순차적 체인 구성
    sequential_chain = (
        summarize_prompt | 
        model | 
        output_parser | 
        {"summary": lambda x: x, "text": lambda x: x} |  # 요약 결과를 다음 단계로 전달
        sentiment_prompt | 
        model | 
        output_parser
    )
    
    return sequential_chain

def main():
    """메인 실행 함수"""
    
    # 테스트 텍스트
    text = """오늘 아침 일어나서 시험 준비를 위해 마지막으로 복습을 했다. 
시험장에 들어가서 문제를 풀 때는 긴장했지만, 평소에 열심히 공부했던 내용들이 잘 기억났다.
시험 시간이 끝나고 답안지를 제출할 때는 자신감이 있었다.
결과를 확인했을 때 만점을 받았다는 것을 알게 되었고, 그 순간 정말 기뻤다.
지난 몇 주 동안 밤늦게까지 공부했던 노력이 결실을 맺은 것 같아 뿌듯했다.
선생님께서도 칭찬해 주셔서 더욱 기쁘고 보람찼다.
이번 경험을 통해 노력하면 반드시 좋은 결과가 따른다는 것을 다시 한번 깨달았다."""
    
    print("=" * 60)
    print("1. 기본 요약 및 감정 분석 체인 (병렬 처리)")
    print("=" * 60)
    
    basic_chain = create_basic_chain()
    basic_result = basic_chain.invoke({"text": text})
    
    print(f"요약: {basic_result['summary']}")
    print(f"감정: {basic_result['sentiment']}")
    
    print("\n" + "=" * 60)
    print("2. JSON Output Parser를 사용한 구조화된 출력")
    print("=" * 60)
    
    json_chain = create_json_chain()
    json_result = json_chain.invoke({"text": text})
    
    print("구조화된 결과:")
    print(json.dumps(json_result, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("3. 순차적 처리 체인 (요약 -> 감정 분석)")
    print("=" * 60)
    
    sequential_chain = create_sequential_chain()
    sequential_result = sequential_chain.invoke({"text": text})
    
    print(f"감정 분석 결과: {sequential_result}")
    
    print("\n" + "=" * 60)
    print("4. 다양한 텍스트로 테스트")
    print("=" * 60)
    
    test_texts = [
        "오늘은 정말 좋은 날씨였다. 친구들과 함께 공원에서 피크닉을 했다. 맛있는 음식도 먹고 재미있는 게임도 했다. 정말 행복한 하루였다.",
        "오늘 시험에서 떨어졌다. 열심히 공부했는데도 결과가 좋지 않아서 정말 속상하다. 앞으로 더 열심히 해야겠다.",
        "오늘은 평범한 하루였다. 아침에 일어나서 출근하고, 저녁에 집에 와서 TV를 봤다. 특별한 일은 없었다."
    ]
    
    for i, test_text in enumerate(test_texts, 1):
        print(f"\n테스트 {i}:")
        print(f"텍스트: {test_text[:50]}...")
        
        result = basic_chain.invoke({"text": test_text})
        print(f"요약: {result['summary']}")
        print(f"감정: {result['sentiment']}")

if __name__ == "__main__":
    main() 