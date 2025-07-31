# PaddleOCR 한글 이미지 인식 AI 서버

## 프로젝트 개요
PaddleOCR을 활용하여 한글 텍스트가 포함된 이미지를 읽고 텍스트를 추출하여 반환하는 AI 서버입니다.

## 주요 기능
- 이미지 업로드 및 처리
- PaddleOCR을 통한 한글 텍스트 인식
- RESTful API 제공
- Swagger UI를 통한 API 문서

## 기술 스택
- **Backend**: FastAPI (Python)
- **OCR Engine**: PaddleOCR
- **패키지 관리**: pip/requirements.txt

## 프로젝트 구조
```
project/
├── main.py
├── ocr_service.py
├── requirements.txt
├── uploads/
├── README.md
└── run.bat
```

## 설치 및 실행
1. Python 3.8+ 설치
2. 의존성 설치: `pip install -r requirements.txt`
3. 서버 실행: `python main.py`
4. API 문서 확인: `http://localhost:8000/docs` 