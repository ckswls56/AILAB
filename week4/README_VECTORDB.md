# 벡터 데이터베이스 실습 (PostgreSQL + pgvector)

이 프로젝트는 PostgreSQL과 pgvector 확장을 사용하여 벡터 데이터베이스를 구축하고, OpenAI 임베딩을 활용한 유사도 검색을 구현합니다.

## 🚀 기능

- **문서 임베딩 저장**: OpenAI 임베딩을 사용하여 텍스트를 벡터로 변환
- **유사도 검색**: 코사인 유사도를 기반으로 한 벡터 검색
- **메타데이터 지원**: JSON 형태의 메타데이터 저장
- **대화형 인터페이스**: 쉬운 사용을 위한 CLI 인터페이스

## 📋 사전 요구사항

1. **Docker & Docker Compose** 설치
2. **Python 3.8+** 설치
3. **OpenAI API 키** 발급

## 🛠️ 설치 및 설정

### 1. PostgreSQL 데이터베이스 시작

```bash
# 프로젝트 루트 디렉토리에서
docker-compose up -d
```

### 2. Python 의존성 설치

```bash
cd week4
pip install -r requirements_vectordb.txt
```

### 3. 환경 변수 설정

`week4` 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🎯 사용법

### 기본 실습 실행

```bash
python vectordb_practice.py
```

### 대화형 데모 실행

```bash
python vectordb_demo.py
```

### Windows에서 실행

```bash
run_vectordb.bat
```

## 📁 파일 구조

```
week4/
├── vectordb_practice.py      # 메인 벡터 데이터베이스 클래스
├── vectordb_demo.py          # 대화형 검색 인터페이스
├── requirements_vectordb.txt # Python 의존성
├── env_example.txt          # 환경 변수 템플릿
├── run_vectordb.bat         # Windows 실행 스크립트
└── README_VECTORDB.md       # 이 파일
```

## 🔧 주요 클래스 및 메서드

### VectorDatabase 클래스

- `__init__()`: 데이터베이스 연결 초기화
- `create_tables()`: 필요한 테이블 및 인덱스 생성
- `add_document()`: 단일 문서 추가
- `add_documents()`: 여러 문서 일괄 추가
- `search_similar()`: 유사도 검색
- `get_all_documents()`: 모든 문서 조회
- `delete_document()`: 문서 삭제

## 🗄️ 데이터베이스 스키마

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX documents_embedding_idx 
ON documents USING ivfflat (embedding vector_cosine_ops);
```

## 🎮 데모 기능

### 1. 문서 추가
- 텍스트 내용과 카테고리 메타데이터 입력
- OpenAI 임베딩으로 벡터 변환 후 저장

### 2. 유사도 검색
- 검색 쿼리를 벡터로 변환
- 코사인 유사도 기반으로 가장 유사한 문서 검색
- 유사도 점수와 함께 결과 표시

### 3. 문서 관리
- 모든 저장된 문서 조회
- 특정 문서 삭제

## 🔍 검색 예시

```
검색 쿼리: "인공지능과 머신러닝의 차이점"

결과:
1. 유사도: 0.8923
   내용: 인공지능은 컴퓨터가 인간의 학습능력과 추론능력...
   메타데이터: {"category": "AI", "doc_id": 1}

2. 유사도: 0.8456
   내용: 머신러닝은 데이터로부터 패턴을 학습하여...
   메타데이터: {"category": "AI", "doc_id": 2}
```

## 🚨 문제 해결

### 데이터베이스 스키마 오류 (metadata 컬럼 없음)
```bash
# 데이터베이스 초기화 (기존 테이블 삭제 후 재생성)
python reset_database.py

# 또는 Windows에서
run_vectordb.bat  # 옵션 1 선택
```

### 데이터베이스 연결 실패
```bash
# PostgreSQL 컨테이너 상태 확인
docker ps

# 컨테이너 재시작
docker-compose restart
```

### OpenAI API 키 오류
- `.env` 파일에 올바른 API 키가 설정되었는지 확인
- API 키의 잔액과 사용량 제한 확인

### 의존성 설치 오류
```bash
# 가상환경 사용 권장
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements_vectordb.txt
```

## 🔗 관련 링크

- [pgvector 공식 문서](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [LangChain 문서](https://python.langchain.com/)


## 📝 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다. 