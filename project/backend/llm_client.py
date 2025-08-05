import os
import httpx
import logging
from typing import List, Dict, Any, Optional
import json
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class InternalLLMClient:
    """내부 LLM API 클라이언트"""
    
    def __init__(self):
        self.base_url = os.getenv("LLM_API_URL", "http://10.231.255.37:11434")
        self.model = os.getenv("LLM_MODEL", "gemma3:27b-it-q4_0")
        self.timeout = 120.0  # LLM 응답 대기 시간
        
        # 로컬 임베딩 모델 (CPU에서 동작, 가벼운 모델 사용)
        # 폐쇄망 환경에서 미리 다운로드한 모델 사용
        default_model_path = "/app/paraphrase-MiniLM-L3-v2" if os.path.exists("/app") else "paraphrase-MiniLM-L3-v2"
        embedding_model_path = os.getenv("LOCAL_EMBEDDING_MODEL", default_model_path)
        
        # 절대 경로로 변환 (상대 경로 시작 문자 제거)
        if embedding_model_path.startswith("./"):
            embedding_model_path = embedding_model_path[2:]
            
        self.embedding_model = SentenceTransformer(embedding_model_path)
        logger.info(f"로컬 임베딩 모델 로드 완료: {embedding_model_path}")
        
    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.0
    ) -> str:
        """채팅 완성 요청"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": temperature
                        }
                    },
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                return result["message"]["content"]
                
        except Exception as e:
            logger.error(f"LLM API 호출 중 오류 발생: {e}")
            raise Exception(f"LLM API 호출 실패: {str(e)}")
    
    def get_embedding(self, text: str) -> List[float]:
        """로컬에서 텍스트 임베딩 생성 (CPU 사용)"""
        try:
            # sentence-transformers로 로컬에서 임베딩 생성
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
                
        except Exception as e:
            logger.error(f"로컬 임베딩 생성 중 오류 발생: {e}")
            # 임베딩 실패 시 더미 벡터 반환
            logger.warning("임베딩 생성 실패, 더미 벡터 사용")
            return [0.0] * 384  # paraphrase-MiniLM-L3-v2의 기본 차원

    def format_messages_for_qa(self, context: str, question: str) -> List[Dict[str, str]]:
        """QA를 위한 메시지 포맷팅"""
        system_prompt = """당신은 전문적인 문서 분석 AI입니다. 제공된 문서들을 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 해주세요.

**답변 지침:**
1. 제공된 문서의 내용만을 바탕으로 답변하세요
2. 문서에서 찾을 수 없는 정보는 "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 명시하세요
3. 답변은 구체적이고 명확하게 작성하세요
4. 관련된 구체적인 정보나 수치가 있다면 포함하세요
5. 한국어로 답변하세요"""

        user_content = f"""**문서 내용:**
{context}

**사용자 질문:**
{question}

**답변:**"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]