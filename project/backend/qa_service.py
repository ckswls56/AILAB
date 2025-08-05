import time
import logging
from typing import List, Optional, Dict, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from models import QuestionResponse, SourceDocument
from llm_client import InternalLLMClient

logger = logging.getLogger(__name__)

class QAService:
    """질의응답 서비스"""
    
    def __init__(self):
        self.llm_client = InternalLLMClient()
    
    async def answer_question(
        self, 
        question: str, 
        document_ids: Optional[List[str]], 
        top_k: int, 
        db: AsyncSession
    ) -> QuestionResponse:
        """질문에 대한 답변 생성"""
        start_time = time.time()
        
        try:
            # 1. 질문을 벡터화 (로컬 CPU에서 처리)
            question_embedding = self.llm_client.get_embedding(question)
            
            # 2. 유사한 문서 청크 검색
            relevant_chunks = await self._search_relevant_chunks(
                question_embedding, document_ids, top_k, db
            )
            
            if not relevant_chunks:
                return QuestionResponse(
                    question=question,
                    answer="질문과 관련된 문서를 찾을 수 없습니다. 문서를 업로드하고 다시 시도해주세요.",
                    source_documents=[],
                    processing_time=time.time() - start_time
                )
            
            # 3. 컨텍스트 구성
            context = self._build_context(relevant_chunks)
            
            # 4. 내부 LLM을 사용하여 답변 생성
            messages = self.llm_client.format_messages_for_qa(context, question)
            answer = await self.llm_client.chat_completion(messages, temperature=0.0)
            
            # 5. 출처 문서 정보 구성
            source_documents = await self._build_source_documents(relevant_chunks, db)
            
            processing_time = time.time() - start_time
            
            return QuestionResponse(
                question=question,
                answer=answer,
                source_documents=source_documents,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"질의응답 처리 중 오류 발생: {e}")
            raise
    
    async def _search_relevant_chunks(
        self, 
        question_embedding: List[float], 
        document_ids: Optional[List[str]], 
        top_k: int, 
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """관련 문서 청크 검색"""
        try:
            # 기본 쿼리
            base_query = """
                SELECT 
                    dc.id,
                    dc.document_id,
                    dc.chunk_index,
                    dc.content,
                    dc.metadata,
                    d.filename,
                    1 - (dc.embedding <=> :question_embedding) as similarity_score
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
            """
            
            # 문서 ID 필터링 추가
            if document_ids:
                base_query += " WHERE dc.document_id = ANY(:document_ids)"
                params = {
                    "question_embedding": f"[{','.join(map(str, question_embedding))}]",
                    "document_ids": document_ids
                }
            else:
                params = {"question_embedding": f"[{','.join(map(str, question_embedding))}]"}
            
            # 유사도 순으로 정렬하고 top_k 개만 선택
            final_query = base_query + """
                ORDER BY similarity_score DESC
                LIMIT :limit
            """
            
            params["limit"] = top_k
            
            result = await db.execute(text(final_query), params)
            
            chunks = []
            for row in result:
                chunks.append({
                    "id": str(row.id),
                    "document_id": str(row.document_id),
                    "chunk_index": row.chunk_index,
                    "content": row.content,
                    "metadata": row.metadata,
                    "filename": row.filename,
                    "similarity_score": float(row.similarity_score)
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"문서 청크 검색 중 오류 발생: {e}")
            raise
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """검색된 청크들로부터 컨텍스트 구성"""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[문서 {i}: {chunk['filename']}]\n{chunk['content']}\n"
            )
        
        return "\n".join(context_parts)
    
    async def _build_source_documents(
        self, 
        chunks: List[Dict[str, Any]], 
        db: AsyncSession
    ) -> List[SourceDocument]:
        """출처 문서 정보 구성"""
        source_documents = []
        
        for chunk in chunks:
            source_documents.append(SourceDocument(
                document_id=chunk["document_id"],
                filename=chunk["filename"],
                chunk_index=chunk["chunk_index"],
                content=chunk["content"][:500] + "..." if len(chunk["content"]) > 500 else chunk["content"],
                similarity_score=chunk["similarity_score"]
            ))
        
        return source_documents