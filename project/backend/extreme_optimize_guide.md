# 🚀 극한 Docker 이미지 최적화 가이드 v2.0

## 🆕 2024 최신 극한 최적화 적용

### 🎯 목표: 8.7GB → 3-4GB (60% 감소)

## ✅ 적용된 극한 최적화

### 1. **Alpine Linux 기반 변경**
```dockerfile
FROM python:3.11-alpine AS builder
FROM python:3.11-alpine
```
- 기본 이미지 크기 **~200MB 절약** (slim 대비)

### 2. **CPU 전용 PyTorch 명시적 우선 설치**
```dockerfile
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```
- GPU 버전 방지로 **~3-4GB 절약**

### 3. **7단계 극한 파일 정리**
```dockerfile
find /opt/venv -name "*.pyc" -delete && \
find /opt/venv -name "tests" -type d -exec rm -rf {} + && \
find /opt/venv -name "test" -type d -exec rm -rf {} + && \
find /opt/venv -name "__pycache__" -type d -exec rm -rf {} + && \
find /opt/venv -name "*.so" -exec strip {} + && \
find /opt/venv -name "*.dist-info" -type d -exec rm -rf {} + && \
find /opt/venv -name "*.egg-info" -type d -exec rm -rf {} +
```
- 메타데이터 및 불필요한 파일 **~1-2GB 절약**

### 4. **런타임 의존성 최소화**
```dockerfile
# Alpine 최소 패키지만 설치
RUN apk add --no-cache libpq libffi openssl
```

### 5. **개선된 .dockerignore**
- 모든 문서, 테스트, 캐시 파일 제외
- **빌드 컨텍스트 90% 감소**

## 📊 예상 결과

| 항목 | 이전 (v1) | 극한 최적화 (v2) | 절약량 |
|------|-----------|------------------|--------|
| **베이스 이미지** | ~1GB | ~200MB | **80% ↓** |
| **venv 크기** | 5.58GB | ~2-2.5GB | **60% ↓** |
| **전체 이미지** | 8.7GB+ | **3-4GB** | **60% ↓** |

## 🚀 간편 빌드 & 분석

### 원클릭 빌드
```bash
cd AILAB/project/backend
./build-optimized.sh
```

### 상세 크기 분석
```bash
./analyze-size.sh
```

## 🔧 수동 빌드
```bash
cd AILAB/project/backend

# BuildKit 활성화로 더 빠른 빌드
export DOCKER_BUILDKIT=1

# 극한 최적화 빌드
docker build --no-cache --compress -t pdf-qa-api:optimized .

# 크기 확인
docker images pdf-qa-api:optimized
```

## 📈 성능 모니터링

### 빌드 시간 vs 크기
- **빌드 시간**: +50% (Alpine 컴파일)
- **이미지 크기**: -60% (극한 최적화)
- **런타임 성능**: 동일

### 메모리 사용량
```bash
docker stats pdf-qa-optimized
```

## 🚨 트러블슈팅

### Alpine 호환성 이슈
```bash
# C 라이브러리 의존성 문제 시
RUN apk add --no-cache musl-dev gcc
```

### 패키지 설치 실패
```bash
# 빌드 로그 확인
docker build --no-cache --progress=plain -t pdf-qa-api:optimized .
```

## 🎯 추가 최적화 옵션

### Distroless (보안 강화)
```dockerfile
FROM gcr.io/distroless/python3-debian11
# 장점: 최고 보안, 더 작은 크기
# 단점: 디버깅 불가, 셸 없음
```

### Multi-arch 빌드
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t pdf-qa-api:multi .
```

## 📋 체크리스트

- [ ] Alpine 기반 Dockerfile 적용
- [ ] .dockerignore 개선
- [ ] CPU 전용 PyTorch 설치 확인
- [ ] 빌드 스크립트 실행
- [ ] 크기 3-4GB 달성 확인
- [ ] 컨테이너 정상 동작 테스트