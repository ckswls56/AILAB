"""
데이터베이스 초기화 스크립트
기존 테이블을 삭제하고 새로운 스키마로 재생성
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def reset_database():
    """데이터베이스 테이블 초기화"""
    
    # 데이터베이스 연결
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "postgres",
        "user": "postgres",
        "password": "123456789"
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        print("✅ 데이터베이스 연결 성공")
        
        with conn.cursor() as cursor:
            # 기존 테이블 삭제
            print("🗑️ 기존 테이블 삭제 중...")
            cursor.execute("DROP TABLE IF EXISTS documents CASCADE;")
            
            # pgvector 확장 활성화
            print("🔧 pgvector 확장 활성화...")
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # 새로운 테이블 생성 (metadata 컬럼 포함)
            print("📋 새로운 테이블 생성 중...")
            cursor.execute("""
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # 벡터 검색을 위한 인덱스 생성
            print("🔍 벡터 인덱스 생성 중...")
            cursor.execute("""
                CREATE INDEX documents_embedding_idx 
                ON documents USING ivfflat (embedding vector_cosine_ops);
            """)
            
            conn.commit()
            print("✅ 데이터베이스 초기화 완료!")
            
            # 테이블 구조 확인
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'documents'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("\n📊 테이블 구조:")
            print("-" * 50)
            for col in columns:
                print(f"{col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    print("🔄 데이터베이스 초기화를 시작합니다...")
    print("=" * 50)
    
    success = reset_database()
    
    if success:
        print("\n🎉 초기화가 완료되었습니다!")
        print("이제 vectordb_practice.py를 실행할 수 있습니다.")
    else:
        print("\n❌ 초기화에 실패했습니다.")
        print("PostgreSQL이 실행 중인지 확인해주세요.") 