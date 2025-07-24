# LCEL (LangChain Expression Language) 실습

이 실습에서는 LCEL을 사용하여 텍스트 요약 및 감정 분석 체인을 구현합니다.

## 📋 요구사항

1. **사용자 입력을 받아 내용을 요약하기**
2. **요약된 내용을 기반으로 감정 분석하기** (긍정, 부정, 중립)
3. **요약된 문장과 감정 분석 결과를 출력하기**
4. **JSON Output Parser로 구조화된 출력으로 변환하기**

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements_lcel.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here  # 선택사항
LANGSMITH_TRACING=true  # 선택사항
LANGCHAIN_PROJECT=your_project_name  # 선택사항
```

### 3. 실행

```bash
python run_lcel_practice.py
```

## 📁 파일 구조

```
week4/
├── lcel_practice.py          # 메인 LCEL 실습 코드
├── run_lcel_practice.py      # 실행 스크립트
├── requirements_lcel.txt     # 의존성 패키지 목록
├── README_LCEL.md           # 이 파일
└── 4.3.LCEL.ipynb           # 원본 노트북
```

## 🔧 구현된 기능

### 1. 기본 요약 및 감정 분석 체인 (병렬 처리)

- `RunnableParallel`을 사용하여 요약과 감정 분석을 동시에 수행
- 각각의 결과를 딕셔너리 형태로 반환

```python
chain = RunnableParallel({
    "summary": summarize_chain,
    "sentiment": sentiment_chain
})
```

### 2. JSON Output Parser를 사용한 구조화된 출력

- Pydantic 모델을 사용하여 출력 스키마 정의
- JSON 형식으로 구조화된 결과 반환

```python
class AnalysisResult(BaseModel):
    summary: str = Field(description="텍스트 요약")
    sentiment: Literal["긍정", "부정", "중립"] = Field(description="감정 분석 결과")
    confidence: float = Field(description="감정 분석 신뢰도 (0.0-1.0)", ge=0.0, le=1.0)
```

### 3. 순차적 처리 체인

- 요약을 먼저 수행한 후, 요약된 내용을 기반으로 감정 분석
- 파이프라인 형태로 데이터 흐름 구성

## 📊 실행 결과 예시

```
============================================================
1. 기본 요약 및 감정 분석 체인 (병렬 처리)
============================================================
요약: 학생이 시험 준비를 열심히 하고 만점을 받아 기뻐하는 내용입니다.
감정: 긍정

============================================================
2. JSON Output Parser를 사용한 구조화된 출력
============================================================
구조화된 결과:
{
  "summary": "학생이 시험 준비를 열심히 하고 만점을 받아 기뻐하는 내용입니다.",
  "sentiment": "긍정",
  "confidence": 0.95
}

============================================================
3. 순차적 처리 체인 (요약 -> 감정 분석)
============================================================
감정 분석 결과: 긍정
```

## 🎯 학습 포인트

1. **LCEL의 파이프 연산자 (`|`) 사용법**
2. **RunnableParallel을 통한 병렬 처리**
3. **Output Parser를 통한 출력 구조화**
4. **Pydantic 모델을 활용한 타입 안전성**
5. **체인 구성의 다양한 패턴**

## 🔍 추가 실습 아이디어

1. **스트리밍 출력**: `.stream()` 메서드를 사용한 실시간 출력
2. **배치 처리**: `.batch()` 메서드를 사용한 여러 텍스트 동시 처리
3. **커스텀 함수**: `RunnableLambda`를 사용한 데이터 전처리/후처리
4. **조건부 분기**: 특정 조건에 따라 다른 체인으로 분기하는 로직

## 📚 참고 자료

- [LangChain LCEL 공식 문서](https://python.langchain.com/docs/expression_language/)
- [LangSmith 관찰성 도구](https://www.langchain.com/langsmith)
- [Pydantic 데이터 검증](https://docs.pydantic.dev/) 