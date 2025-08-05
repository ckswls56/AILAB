from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class QuestionRequest(BaseModel):
    """질문 요청 모델"""
    question: str = Field(..., description="사용자 질문")
    document_ids: Optional[List[str]] = Field(None, description="검색할 문서 ID 목록 (None이면 모든 문서에서 검색)")
    top_k: int = Field(default=5, ge=1, le=20, description="검색할 문서 청크 수")

class SourceDocument(BaseModel):
    """출처 문서 정보"""
    document_id: str
    filename: str
    chunk_index: int
    content: str
    similarity_score: float

class QuestionResponse(BaseModel):
    """질문 응답 모델"""
    question: str
    answer: str
    source_documents: List[SourceDocument]
    processing_time: float

class DocumentInfo(BaseModel):
    """문서 정보 모델"""
    id: str
    filename: str
    content_preview: str = Field(..., description="문서 내용 미리보기 (첫 200자)")
    chunks_count: int
    created_at: datetime

class DocumentChunk(BaseModel):
    """문서 청크 모델"""
    id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = {}

class UploadResponse(BaseModel):
    """업로드 응답 모델"""
    success: bool
    message: str
    document_id: str
    chunks_count: int

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str
    detail: str
    status_code: int

class FileUploadResult(BaseModel):
    """개별 파일 업로드 결과"""
    filename: str
    success: bool
    message: str
    document_id: Optional[str] = None
    chunks_count: Optional[int] = None
    error: Optional[str] = None

class MultipleUploadResponse(BaseModel):
    """다중 파일 업로드 응답"""
    total_files: int
    successful_uploads: int
    failed_uploads: int
    results: List[FileUploadResult]
    processing_time: float