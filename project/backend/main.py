from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import os
import shutil
import tempfile
import time
from datetime import datetime

from database import get_db, init_db
from pdf_processor import PDFProcessor
from qa_service import QAService
from models import QuestionRequest, QuestionResponse, DocumentInfo, FileUploadResult, MultipleUploadResponse

app = FastAPI(
    title="PDF 질의응답 AI 서버",
    description="여러 PDF 문서를 업로드하고 질의응답을 수행하는 AI 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
pdf_processor = PDFProcessor()
qa_service = QAService()

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 데이터베이스 초기화"""
    await init_db()

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "PDF 질의응답 AI 서버가 실행 중입니다."}

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    # OCR 상태 확인
    ocr_info = {"status": "unknown"}
    
    try:
        from pdf_processor import OCR_AVAILABLE
        if OCR_AVAILABLE:
            try:
                import pytesseract
                from pdf2image import convert_from_path
                
                # Tesseract 명령어 실행 테스트
                version = pytesseract.get_tesseract_version()
                langs = pytesseract.get_languages()
                
                ocr_info = {
                    "status": "available",
                    "tesseract_version": str(version),
                    "languages": langs,
                    "korean_support": "kor" in langs
                }
            except Exception as e:
                ocr_info = {
                    "status": "error",
                    "error": str(e)
                }
        else:
            ocr_info = {"status": "packages_not_installed"}
    except ImportError as e:
        ocr_info = {"status": "import_error", "error": str(e)}
    
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "ocr": ocr_info
    }

@app.get("/test-ocr")
async def test_ocr():
    """OCR 기능 테스트 엔드포인트"""
    try:
        from pdf_processor import OCR_AVAILABLE, PDFProcessor
        
        if not OCR_AVAILABLE:
            return {"status": "error", "message": "OCR 패키지가 설치되지 않았습니다."}
        
        # OCR 테스트
        try:
            import pytesseract
            from pdf2image import convert_from_path
            from PIL import Image
            import numpy as np
            
            # 실제 텍스트가 있는 테스트 이미지 생성
            from PIL import ImageDraw, ImageFont
            
            test_image = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(test_image)
            
            # 텍스트 그리기 (기본 폰트 사용)
            text = "Hello World! OCR Test 123"
            try:
                # 기본 폰트로 텍스트 그리기
                draw.text((20, 50), text, fill='black')
            except:
                # 폰트 오류 시 간단한 방법
                draw.text((20, 50), text, fill='black')
            
            # OCR 테스트
            test_result = pytesseract.image_to_string(test_image, lang='eng')
            
            # 언어 지원 확인
            available_langs = pytesseract.get_languages()
            
            return {
                "status": "success",
                "message": "OCR 테스트 성공",
                "tesseract_available": True,
                "pdf2image_available": True,
                "test_result": f"OCR 결과: '{test_result.strip()}'",
                "ocr_result_length": len(test_result.strip()),
                "available_languages": available_langs,
                "korean_support": "kor" in available_langs
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"OCR 테스트 실패: {e}",
                "error_type": type(e).__name__
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"OCR 모듈 import 실패: {e}"
        }

@app.post("/upload-pdf", response_model=Dict[str, Any])
async def upload_pdf(
    file: UploadFile = File(...),
    db=Depends(get_db)
):
    """PDF 파일 업로드 및 벡터화"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")
    
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        # PDF 처리 및 벡터화
        result = await pdf_processor.process_pdf(tmp_path, file.filename, db)
        
        # 임시 파일 삭제
        os.unlink(tmp_path)
        
        return {
            "success": True,
            "message": f"PDF '{file.filename}' 처리가 완료되었습니다.",
            "document_id": result["document_id"],
            "chunks_count": result["chunks_count"],
            "extraction_method": result.get("extraction_method", "Standard"),
            "content_length": result.get("content_length", 0),
            "original_content_length": result.get("original_content_length", 0)
        }
    
    except ValueError as ve:
        # PDF 처리 관련 검증 오류 (사용자가 이해할 수 있는 오류)
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        logger.error(f"PDF '{file.filename}' 검증 실패: {ve}")
        raise HTTPException(status_code=400, detail=f"PDF 처리 실패: {str(ve)}")
    
    except Exception as e:
        # 기타 예상치 못한 오류
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        logger.error(f"PDF '{file.filename}' 처리 중 예상치 못한 오류: {e}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류가 발생했습니다. 다른 PDF로 시도해보세요.")

@app.post("/upload-multiple-pdfs", response_model=MultipleUploadResponse)
async def upload_multiple_pdfs(
    files: List[UploadFile] = File(...),
    db=Depends(get_db)
):
    """여러 PDF 파일을 한 번에 업로드 및 벡터화"""
    start_time = time.time()
    results = []
    successful_uploads = 0
    failed_uploads = 0
    
    for file in files:
        result = FileUploadResult(
            filename=file.filename,
            success=False,
            message="",
            document_id=None,
            chunks_count=None,
            error=None
        )
        
        try:
            # PDF 파일 검증
            if not file.filename.endswith('.pdf'):
                result.error = "PDF 파일만 업로드 가능합니다."
                result.message = f"파일 '{file.filename}': PDF 파일이 아닙니다."
                failed_uploads += 1
                results.append(result)
                continue
            
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                # PDF 처리 및 벡터화
                process_result = await pdf_processor.process_pdf(tmp_path, file.filename, db)
                
                # 성공 결과 설정
                result.success = True
                extraction_method = process_result.get("extraction_method", "Standard")
                chunks_count = process_result["chunks_count"]
                content_length = process_result.get("content_length", 0)
                result.message = f"파일 '{file.filename}' 처리 완료: {chunks_count}개 청크 생성 ({extraction_method}, {content_length}자)"
                result.document_id = process_result["document_id"]
                result.chunks_count = chunks_count
                successful_uploads += 1
                
            finally:
                # 임시 파일 삭제
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
        except Exception as e:
            # 실패 결과 설정
            result.error = str(e)
            result.message = f"파일 '{file.filename}' 처리 중 오류가 발생했습니다."
            failed_uploads += 1
        
        results.append(result)
    
    processing_time = time.time() - start_time
    
    return MultipleUploadResponse(
        total_files=len(files),
        successful_uploads=successful_uploads,
        failed_uploads=failed_uploads,
        results=results,
        processing_time=processing_time
    )

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    db=Depends(get_db)
):
    """질문에 대한 답변 생성"""
    try:
        response = await qa_service.answer_question(
            question=request.question,
            document_ids=request.document_ids,
            top_k=request.top_k,
            db=db
        )
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"질문 처리 중 오류가 발생했습니다: {str(e)}")

@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents(db=Depends(get_db)):
    """업로드된 문서 목록 조회"""
    try:
        documents = await pdf_processor.get_documents_list(db)
        return documents
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 목록 조회 중 오류가 발생했습니다: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str, db=Depends(get_db)):
    """문서 삭제"""
    try:
        result = await pdf_processor.delete_document(document_id, db)
        if result:
            return {"success": True, "message": "문서가 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 삭제 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)