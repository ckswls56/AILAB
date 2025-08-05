#!/bin/bash

# 🚀 극한 최적화 Docker 빌드 스크립트

echo "🚀 극한 최적화 Docker 이미지 빌드 시작..."

# 현재 디렉토리 확인
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile이 없습니다. backend 디렉토리에서 실행하세요."
    exit 1
fi

# 기존 이미지 제거 (캐시 완전 정리)
echo "🗑️ 기존 이미지 및 캐시 정리..."
docker rmi pdf-qa-api:optimized 2>/dev/null || true
docker system prune -f

# BuildKit 활성화 (더 효율적인 빌드)
export DOCKER_BUILDKIT=1

echo "🔨 이미지 빌드 중... (시간이 오래 걸릴 수 있습니다)"
docker build \
    --no-cache \
    --compress \
    --squash \
    -t pdf-qa-api:optimized \
    .

if [ $? -ne 0 ]; then
    echo "❌ 빌드 실패!"
    exit 1
fi

echo "✅ 빌드 완료!"

# 이미지 크기 확인
echo ""
echo "📊 이미지 크기 분석:"
docker images pdf-qa-api:optimized

# 레이어별 크기 분석
echo ""
echo "🔍 레이어별 크기 분석:"
docker history pdf-qa-api:optimized

# 가상환경 크기 확인
echo ""
echo "📦 가상환경 크기:"
docker run --rm pdf-qa-api:optimized du -sh /opt/venv

# 전체 크기 비교
echo ""
echo "🎯 크기 비교 요약:"
echo "- 목표: 3-4GB (이전 8.7GB 대비 60% 감소)"
SIZE=$(docker images pdf-qa-api:optimized --format "table {{.Size}}" | tail -1)
echo "- 현재: $SIZE"

echo ""
echo "🚀 최적화 완료! 컨테이너 실행 방법:"
echo "docker run -d -p 8000:8000 --name pdf-qa-optimized pdf-qa-api:optimized"