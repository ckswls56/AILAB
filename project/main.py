import os
import logging
import time
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ocr_service import OCRService

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OCR 서비스 초기화
ocr_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    global ocr_service
    try:
        logger.info("OCR 서비스 초기화 중...")
        ocr_service = OCRService(use_gpu=False)  # GPU 사용하지 않음
        logger.info("OCR 서비스 초기화 완료")
        yield
    except Exception as e:
        logger.error(f"OCR 서비스 초기화 실패: {e}")
        raise
    finally:
        logger.info("OCR 서비스 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="PaddleOCR 한글 이미지 인식 API",
    description="PaddleOCR을 사용하여 한글 텍스트가 포함된 이미지를 읽고 텍스트를 추출하는 API 서버",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 업로드 디렉토리 생성
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "PaddleOCR 한글 이미지 인식 API 서버",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "ocr_service": "ready" if ocr_service else "not_ready"
    }

@app.post("/ocr/upload")
async def ocr_upload(
    file: UploadFile = File(..., description="이미지 파일"),
    include_bbox: bool = Form(False, description="바운딩 박스 정보 포함 여부")
):
    """
    이미지 파일을 업로드하여 OCR 처리
    
    Args:
        file: 업로드할 이미지 파일
        include_bbox: 바운딩 박스 정보 포함 여부
        
    Returns:
        OCR 처리 결과
    """
    try:
        # 파일 유효성 검사
        if not file:
            raise HTTPException(status_code=400, detail="파일이 제공되지 않았습니다")
        
        # 파일 확장자 검사
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(allowed_extensions)}"
            )
        
        # 파일 크기 검사 (10MB 제한)
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="파일 크기가 10MB를 초과합니다")
        
        logger.info(f"파일 업로드: {file.filename}, 크기: {file_size} bytes")
        
        # OCR 처리
        start_time = time.time()
        result = ocr_service.extract_text_from_bytes(file_content)
        processing_time = time.time() - start_time
        
        # 응답 데이터 구성
        response_data = {
            "success": result["success"],
            "filename": file.filename,
            "file_size": file_size,
            "processing_time": round(processing_time, 3),
            "message": result.get("message", ""),
            "text": result.get("text", ""),
            "word_count": result.get("word_count", 0),
            "character_count": result.get("character_count", 0)
        }
        
        # 바운딩 박스 정보 포함 여부
        if include_bbox and result.get("words"):
            response_data["words"] = result["words"]
        
        # 에러가 있는 경우
        if not result["success"]:
            response_data["error"] = result.get("error", "")
            return JSONResponse(
                status_code=500,
                content=response_data
            )
        
        logger.info(f"OCR 처리 완료: {file.filename}, 처리시간: {processing_time:.3f}초")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR 처리 중 오류 발생: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "서버 내부 오류가 발생했습니다"
            }
        )

@app.post("/ocr/path")
async def ocr_from_path(
    image_path: str = Form(..., description="이미지 파일 경로"),
    include_bbox: bool = Form(False, description="바운딩 박스 정보 포함 여부")
):
    """
    로컬 이미지 파일 경로를 사용하여 OCR 처리
    
    Args:
        image_path: 이미지 파일 경로
        include_bbox: 바운딩 박스 정보 포함 여부
        
    Returns:
        OCR 처리 결과
    """
    try:
        # 파일 존재 확인
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {image_path}")
        
        # 파일 크기 확인
        file_size = os.path.getsize(image_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="파일 크기가 10MB를 초과합니다")
        
        logger.info(f"파일 경로 OCR 처리: {image_path}, 크기: {file_size} bytes")
        
        # OCR 처리
        start_time = time.time()
        result = ocr_service.extract_text(image_path)
        processing_time = time.time() - start_time
        
        # 응답 데이터 구성
        response_data = {
            "success": result["success"],
            "image_path": image_path,
            "file_size": file_size,
            "processing_time": round(processing_time, 3),
            "message": result.get("message", ""),
            "text": result.get("text", ""),
            "word_count": result.get("word_count", 0),
            "character_count": result.get("character_count", 0)
        }
        
        # 바운딩 박스 정보 포함 여부
        if include_bbox and result.get("words"):
            response_data["words"] = result["words"]
        
        # 에러가 있는 경우
        if not result["success"]:
            response_data["error"] = result.get("error", "")
            return JSONResponse(
                status_code=500,
                content=response_data
            )
        
        logger.info(f"OCR 처리 완료: {image_path}, 처리시간: {processing_time:.3f}초")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OCR 처리 중 오류 발생: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "서버 내부 오류가 발생했습니다"
            }
        )

@app.get("/info")
async def get_info():
    """서버 정보 조회"""
    return {
        "server_name": "PaddleOCR 한글 이미지 인식 API",
        "version": "1.0.0",
        "supported_formats": ["jpg", "jpeg", "png", "bmp", "tiff", "tif"],
        "max_file_size": "10MB",
        "language": "korean",
        "ocr_engine": "PaddleOCR",
        "endpoints": {
            "upload": "/ocr/upload",
            "path": "/ocr/path",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 