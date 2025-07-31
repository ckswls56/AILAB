"""
벡터 데이터베이스 데모: 간단한 검색 인터페이스
"""

from vectordb_practice import VectorDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def interactive_search():
    """대화형 검색 인터페이스"""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY 환경 변수를 설정해주세요!")
        print("env_example.txt 파일을 참고하여 .env 파일을 생성하세요.")
        return
    
    print("🔍 벡터 데이터베이스 검색 데모")
    print("=" * 50)
    
    # 벡터 데이터베이스 초기화
    vectordb = VectorDatabase()
    
    # 테이블 생성 확인
    if not vectordb.create_tables():
        print("❌ 데이터베이스 연결에 실패했습니다.")
        print("PostgreSQL이 실행 중인지 확인하세요: docker-compose up -d")
        return
    
    print("✅ 데이터베이스 연결 성공!")
    
    while True:
        print("\n" + "=" * 50)
        print("1. 문서 추가")
        print("2. 문서 검색")
        print("3. 모든 문서 보기")
        print("4. 문서 삭제")
        print("5. 종료")
        print("=" * 50)
        
        choice = input("선택하세요 (1-5): ").strip()
        
        if choice == "1":
            content = input("문서 내용을 입력하세요: ").strip()
            if content:
                category = input("카테고리를 입력하세요 (선택사항): ").strip()
                metadata = {"category": category} if category else None
                
                if vectordb.add_document(content, metadata):
                    print("✅ 문서가 성공적으로 추가되었습니다!")
                else:
                    print("❌ 문서 추가에 실패했습니다.")
        
        elif choice == "2":
            query = input("검색할 내용을 입력하세요: ").strip()
            if query:
                top_k = input("검색 결과 개수를 입력하세요 (기본값: 5): ").strip()
                top_k = int(top_k) if top_k.isdigit() else 5
                
                print(f"\n🔍 '{query}' 검색 결과:")
                print("-" * 40)
                
                results = vectordb.search_similar(query, top_k)
                
                if results:
                    for i, result in enumerate(results, 1):
                        print(f"{i}. 유사도: {result['similarity']:.4f}")
                        print(f"   내용: {result['content']}")
                        print(f"   메타데이터: {result['metadata']}")
                        print()
                else:
                    print("검색 결과가 없습니다.")
        
        elif choice == "3":
            print("\n📚 모든 문서:")
            print("-" * 40)
            
            all_docs = vectordb.get_all_documents()
            
            if all_docs:
                for doc in all_docs:
                    print(f"ID: {doc['id']}")
                    print(f"내용: {doc['content']}")
                    print(f"메타데이터: {doc['metadata']}")
                    print(f"생성일: {doc['created_at']}")
                    print("-" * 20)
            else:
                print("저장된 문서가 없습니다.")
        
        elif choice == "4":
            doc_id = input("삭제할 문서 ID를 입력하세요: ").strip()
            if doc_id.isdigit():
                if vectordb.delete_document(int(doc_id)):
                    print("✅ 문서가 성공적으로 삭제되었습니다!")
                else:
                    print("❌ 문서 삭제에 실패했습니다.")
            else:
                print("❌ 올바른 문서 ID를 입력하세요.")
        
        elif choice == "5":
            print("👋 데모를 종료합니다.")
            break
        
        else:
            print("❌ 올바른 선택지를 입력하세요 (1-5).")

if __name__ == "__main__":
    interactive_search() 