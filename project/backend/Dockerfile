# 🚀 극한 최적화 Multi-stage build (안정성 개선)
FROM python:3.11-slim AS builder

WORKDIR /app

# 빌드 도구 설치 (최소한만)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 🎯 안정적인 패키지 설치 (의존성 보존)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --trusted-host files.pythonhosted.org --no-cache-dir -r requirements.txt && \
    pip install --trusted-host download.pytorch.org --no-cache-dir \
        torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 \
        --index-url https://download.pytorch.org/whl/cpu || \
    pip install --no-cache-dir torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1

# 🗑️ 극한 정리: 불필요한 파일들 제거 (더 강화)
RUN find /opt/venv -name "*.pyc" -delete && \
    pip cache purge

# 🏭 Production stage - 최소 런타임
FROM python:3.11-slim

WORKDIR /app

# 런타임 의존성만 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libffi8 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 🧹 최종 정리 한번 더
RUN find /opt/venv -name "*.pyc" -delete

# Copy application code (only production files)
COPY main.py pdf_processor.py qa_service.py database.py models.py llm_client.py ./

# Create directories
RUN mkdir -p uploads data

# Create non-root user for security (Debian 스타일)
RUN useradd --create-home --shell /bin/sh app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Optimized health check (lighter)
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=2 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8000), timeout=5)" || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]