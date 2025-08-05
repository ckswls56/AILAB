# 내부 LLM API 마이그레이션 가이드

## ✅ 완료된 변경사항

### 1. 새로 추가된 파일
- `llm_client.py`: 내부 LLM API 클라이언트 (Ollama/vLLM 호환)

### 2. 수정된 파일
- `qa_service.py`: OpenAI → 내부 LLM API로 변경
- `pdf_processor.py`: OpenAI Embeddings → 내부 임베딩 API로 변경  
- `requirements.txt`: OpenAI 라이브러리 제거, httpx 추가
- `env.example`: OpenAI 설정 제거, 내부 LLM 설정 추가

## 🔧 새로운 환경변수 설정

```bash
# 내부 LLM API 설정 (채팅 전용)
LLM_API_URL=http://10.231.255.37:11434   # 내부 LLM 서버 주소
LLM_MODEL=gemma3:27b-it-q4_0             # 사용할 LLM 모델

# 로컬 임베딩 모델 (CPU에서 동작)
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2   # sentence-transformers 모델
```

## 🚀 배포 전 확인사항

### 1. 내부 LLM 서버 준비
- Ollama 또는 vLLM 서버가 실행 중이어야 함
- `gemma3:27b-it-q4_0` 모델이 다운로드되어 있어야 함
- ⚠️ **임베딩은 로컬 CPU에서 처리** (내부 서버 불필요)

### 2. API 엔드포인트 확인
```bash
# LLM 채팅 테스트 (임베딩은 로컬에서 처리하므로 테스트 불필요)
curl -X POST http://10.231.255.37:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma3:27b-it-q4_0",
    "messages": [{"role": "user", "content": "안녕하세요"}],
    "stream": false
  }'
```

### 3. 의존성 설치
```bash
pip install httpx>=0.25.0 sentence-transformers>=2.2.0
```

## 🔄 기존 OpenAI 설정 제거
- ❌ `OPENAI_API_KEY` 환경변수 불필요
- ❌ `langchain-openai` 라이브러리 제거됨
- ❌ OpenAI API 비용 발생하지 않음

## 📈 성능 최적화 팁
- **채팅**: 내부 LLM 서버에서 처리 (GPU 권장)
- **임베딩**: 로컬 CPU에서 처리 (GPU 불필요)
- 임베딩 모델 변경 가능: `all-MiniLM-L6-v2` (기본), `all-mpnet-base-v2` (고성능)
- 타임아웃 설정: 120초 (조정 가능)

## 🐛 트러블슈팅

### LLM 채팅 오류 시
1. LLM 서버 상태 확인
2. `LLM_API_URL` 설정 확인  
3. 방화벽/포트 설정 확인

### 임베딩 오류 시
1. `sentence-transformers` 설치 확인
2. 임베딩 모델 다운로드 상태 확인
3. 메모리 부족 여부 확인 (CPU RAM)

### 첫 실행 시 임베딩 모델 자동 다운로드
- `all-MiniLM-L6-v2` 모델이 자동으로 다운로드됩니다 (~80MB)
- 인터넷 연결이 필요합니다

## 📋 API 엔드포인트

### 📁 파일 업로드

#### 1. 단일 파일 업로드
```bash
POST /upload-pdf
Content-Type: multipart/form-data

# 응답
{
  "success": true,
  "message": "PDF 'document.pdf' 처리가 완료되었습니다.",
  "document_id": "uuid-string",
  "chunks_count": 25
}
```

#### 2. 다중 파일 업로드 🆕
```bash
POST /upload-multiple-pdfs
Content-Type: multipart/form-data

# 응답
{
  "total_files": 3,
  "successful_uploads": 2,
  "failed_uploads": 1,
  "processing_time": 45.2,
  "results": [
    {
      "filename": "doc1.pdf",
      "success": true,
      "message": "파일 'doc1.pdf' 처리가 완료되었습니다.",
      "document_id": "uuid1",
      "chunks_count": 20,
      "error": null
    },
    {
      "filename": "doc2.pdf",
      "success": true,
      "message": "파일 'doc2.pdf' 처리가 완료되었습니다.",
      "document_id": "uuid2", 
      "chunks_count": 15,
      "error": null
    },
    {
      "filename": "invalid.txt",
      "success": false,
      "message": "파일 'invalid.txt': PDF 파일이 아닙니다.",
      "document_id": null,
      "chunks_count": null,
      "error": "PDF 파일만 업로드 가능합니다."
    }
  ]
}
```

### 💬 질의응답
```bash
POST /ask
Content-Type: application/json

{
  "question": "계약서의 주요 조건은 무엇인가요?",
  "document_ids": ["uuid1", "uuid2"], // 선택적
  "top_k": 5
}
```

### 📚 문서 관리
```bash
GET /documents        # 문서 목록 조회
DELETE /documents/{id} # 문서 삭제
```

## 🐳 Docker 이미지 최적화

### ⚡ **최적화된 Dockerfile 특징**

1. **Multi-stage Build**: 빌드용/런타임용 분리
2. **CPU-only PyTorch**: GPU 버전 대비 ~5GB 절약
3. **경량 임베딩 모델**: `paraphrase-MiniLM-L3-v2` (~50MB)
4. **가상환경 사용**: 깔끔한 의존성 관리
5. **보안 강화**: non-root 사용자 실행

### 📏 **이미지 크기 비교**

| 버전 | 크기 | 설명 |
|------|------|------|
| ❌ **기존** | ~10GB | GPU PyTorch + 큰 모델 |
| ✅ **최적화** | ~1.5GB | CPU PyTorch + 경량 모델 |

### 🚀 **빌드 명령어**

```bash
# 백엔드 디렉토리에서 빌드
cd project/backend
docker build -t pdf-qa-api:optimized .

# 이미지 크기 확인
docker images pdf-qa-api:optimized
```

### 🔧 **추가 최적화 옵션**

#### 1. 더 가벼운 임베딩 모델
```bash
# 환경변수로 모델 변경 가능
LOCAL_EMBEDDING_MODEL=paraphrase-MiniLM-L3-v2  # ~50MB (기본)
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2         # ~80MB (더 정확)
LOCAL_EMBEDDING_MODEL=distiluse-base-multilingual-cased  # 다국어
```

#### 2. Alpine 기반 (더 작게)
```dockerfile
# 더 작은 이미지가 필요하면 Alpine 사용
FROM python:3.11-alpine
# 단, 컴파일 시간이 더 오래 걸림
```

### 🐛 **빌드 트러블슈팅**

#### 캐시 문제 시
```bash
docker build --no-cache -t pdf-qa-api:optimized .
```

#### 메모리 부족 시
```bash
# Docker Desktop에서 메모리 할당량 증가 (8GB 이상 권장)
docker build --memory=8g -t pdf-qa-api:optimized .
```