import os
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)

# 환경 변수에서 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pdf_qa_user:pdf_qa_password@localhost:5432/pdf_qa_db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# SQLAlchemy 엔진 및 세션 설정
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=NullPool,
    echo=True
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """데이터베이스 세션 의존성"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """데이터베이스 초기화"""
    try:
        # pgvector 확장 설치 및 테이블 생성
        async with engine.begin() as conn:
            # pgvector 확장 설치
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # 기존 테이블 삭제 (차원 불일치 문제 해결)
            await conn.execute(text("DROP TABLE IF EXISTS document_chunks CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS documents CASCADE"))
            
            # 문서 테이블 생성
            await conn.execute(text("""
                CREATE TABLE documents (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    filename VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 문서 청크 테이블 생성 (384차원 embedding)
            await conn.execute(text("""
                CREATE TABLE document_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(384),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # 인덱스 생성 (벡터 유사도 검색용)
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
                ON document_chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            
            # 문서 ID 인덱스
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS document_chunks_document_id_idx 
                ON document_chunks(document_id)
            """))
            
        logger.info("데이터베이스 초기화가 완료되었습니다.")
        
    except Exception as e:
        logger.error(f"데이터베이스 초기화 중 오류 발생: {e}")
        raise

async def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"데이터베이스 연결 테스트 실패: {e}")
        return False