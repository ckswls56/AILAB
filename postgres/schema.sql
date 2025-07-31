-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 예시 테이블 생성
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536), -- OpenAI 임베딩 차원
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 벡터 검색을 위한 인덱스 생성
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents USING ivfflat (embedding vector_cosine_ops);

-- 샘플 데이터 삽입 (선택사항)
INSERT INTO documents (content, embedding) VALUES 
('안녕하세요! 이것은 샘플 문서입니다.', '[0.1, 0.2, 0.3, ...]'::vector); 