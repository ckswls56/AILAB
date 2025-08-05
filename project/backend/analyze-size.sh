#!/bin/bash

# 🔍 Docker 이미지 크기 상세 분석 스크립트

echo "🔍 Docker 이미지 크기 상세 분석..."

if ! docker images pdf-qa-api:optimized | grep -q optimized; then
    echo "❌ pdf-qa-api:optimized 이미지가 없습니다. 먼저 빌드하세요."
    exit 1
fi

echo ""
echo "📊 기본 이미지 정보:"
docker images pdf-qa-api:optimized

echo ""
echo "🏗️ 레이어별 크기 (상위 10개):"
docker history pdf-qa-api:optimized --format "table {{.CreatedSince}}\t{{.Size}}\t{{.CreatedBy}}" | head -11

echo ""
echo "📦 주요 디렉토리 크기:"
echo "가상환경 전체:"
docker run --rm pdf-qa-api:optimized du -sh /opt/venv
echo ""
echo "가상환경 내부 상위 10개:"
docker run --rm pdf-qa-api:optimized du -sh /opt/venv/* | sort -hr | head -10

echo ""
echo "🐍 Python 패키지별 크기 (상위 15개):"
docker run --rm pdf-qa-api:optimized find /opt/venv/lib/python3.11/site-packages -maxdepth 1 -type d -exec du -sh {} + | sort -hr | head -15

echo ""
echo "🗂️ 애플리케이션 파일 크기:"
docker run --rm pdf-qa-api:optimized du -sh /app/*

echo ""
echo "💾 전체 시스템 사용량:"
docker run --rm pdf-qa-api:optimized df -h

echo ""
echo "🎯 최적화 제안:"
echo "1. 가장 큰 패키지들 확인"
echo "2. 불필요한 의존성 제거 검토"
echo "3. 더 작은 베이스 이미지 고려"