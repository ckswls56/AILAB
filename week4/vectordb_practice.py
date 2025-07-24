"""
벡터 데이터베이스 실습: PostgreSQL + pgvector
1. PostgreSQL 연결 및 pgvector 확장 사용
2. 문서 임베딩 저장 및 검색
3. 유사도 검색 구현
4. OpenAI 임베딩과 연동
"""

import psycopg2
import numpy as np
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import json
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def vector_to_string(vector):
    """벡터를 PostgreSQL vector 타입 문자열로 변환"""
    if isinstance(vector, list):
        return f"[{','.join(map(str, vector))}]"
    elif hasattr(vector, 'tolist'):
        return f"[{','.join(map(str, vector.tolist()))}]"
    else:
        return str(vector)

class VectorDatabase:
    """PostgreSQL + pgvector를 사용한 벡터 데이터베이스 클래스"""
    
    def __init__(self, host="localhost", port=5432, database="postgres", 
                 user="postgres", password="123456789"):
        """데이터베이스 연결 초기화"""
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
    def connect(self):
        """데이터베이스 연결"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except Exception as e:
            print(f"데이터베이스 연결 실패: {e}")
            return None
    
    def create_tables(self):
        """필요한 테이블 생성"""
        conn = self.connect()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                # pgvector 확장 활성화
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                
                # 문서 테이블 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL,
                        metadata JSONB,
                        embedding vector(1536),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # 벡터 검색을 위한 인덱스 생성
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS documents_embedding_idx 
                    ON documents USING ivfflat (embedding vector_cosine_ops);
                """)
                
                conn.commit()
                print("테이블 생성 완료")
                return True
                
        except Exception as e:
            print(f"테이블 생성 실패: {e}")
            return False
        finally:
            conn.close()
    
    def add_document(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """문서 추가"""
        try:
            # 임베딩 생성
            embedding = self.embeddings.embed_query(content)
            
            conn = self.connect()
            if not conn:
                return False
                
            with conn.cursor() as cursor:
                vector_str = vector_to_string(embedding)
                cursor.execute("""
                    INSERT INTO documents (content, metadata, embedding)
                    VALUES (%s, %s, %s::vector)
                """, (content, json.dumps(metadata) if metadata else None, vector_str))
                
                conn.commit()
                print(f"문서 추가 완료: {content[:50]}...")
                return True
                
        except Exception as e:
            print(f"문서 추가 실패: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """유사도 검색"""
        try:
            # 쿼리 임베딩 생성
            query_embedding = self.embeddings.embed_query(query)
            
            conn = self.connect()
            if not conn:
                return []
                
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query_vector_str = vector_to_string(query_embedding)
                cursor.execute("""
                    SELECT id, content, metadata, 
                           1 - (embedding <=> %s::vector) as similarity
                    FROM documents
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                """, (query_vector_str, query_vector_str, top_k))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            print(f"검색 실패: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """모든 문서 조회"""
        try:
            conn = self.connect()
            if not conn:
                return []
                
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, content, metadata, created_at
                    FROM documents
                    ORDER BY created_at DESC
                """)
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except Exception as e:
            print(f"문서 조회 실패: {e}")
            return []
        finally:
            if conn:
                conn.close()

def main():
    """메인 실행 함수"""
    
    # OpenAI API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY 환경 변수를 설정해주세요!")
        return
    
    # 벡터 데이터베이스 초기화
    vectordb = VectorDatabase()
    
    print("=" * 60)
    print("벡터 데이터베이스 초기화")
    print("=" * 60)
    
    # 테이블 생성
    if not vectordb.create_tables():
        print("테이블 생성에 실패했습니다.")
        return
    
    print("\n" + "=" * 60)
    print("샘플 문서 추가")
    print("=" * 60)
    
    # 샘플 문서들
    sample_documents = [
        "인공지능은 컴퓨터가 인간의 학습능력과 추론능력, 지각능력, 자연언어의 이해능력 등을 인공적으로 구현한 기술입니다.",
        "머신러닝은 데이터로부터 패턴을 학습하여 예측이나 분류를 수행하는 인공지능의 한 분야입니다.",
        "딥러닝은 인공신경망을 기반으로 한 머신러닝 기법으로, 복잡한 패턴을 학습할 수 있습니다.",
        "자연어처리는 인간의 언어를 컴퓨터가 이해하고 처리할 수 있도록 하는 기술입니다.",
        "컴퓨터 비전은 컴퓨터가 디지털 이미지나 비디오로부터 의미 있는 정보를 추출하고 이해하는 기술입니다."
    ]
    
    # 문서 추가
    for i, doc in enumerate(sample_documents, 1):
        metadata = {"category": "AI", "doc_id": i}
        vectordb.add_document(doc, metadata)
    
    print("\n" + "=" * 60)
    print("모든 문서 조회")
    print("=" * 60)
    
    all_docs = vectordb.get_all_documents()
    for doc in all_docs:
        print(f"ID: {doc['id']}, 내용: {doc['content'][:50]}...")
    
    print("\n" + "=" * 60)
    print("유사도 검색 테스트")
    print("=" * 60)
    
    # 검색 쿼리들
    search_queries = [
        "인공지능과 머신러닝의 차이점",
        "자연어 처리 기술",
        "데이터 분석 방법"
    ]
    
    for query in search_queries:
        print(f"\n검색 쿼리: {query}")
        print("-" * 40)
        
        results = vectordb.search_similar(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. 유사도: {result['similarity']:.4f}")
            print(f"   내용: {result['content']}")
            print(f"   메타데이터: {result['metadata']}")
            print()

if __name__ == "__main__":
    main() 