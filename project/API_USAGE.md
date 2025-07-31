# PaddleOCR 한글 이미지 인식 API 사용법

## 서버 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python main.py
```

또는 Windows에서:
```bash
run.bat
```

서버가 시작되면 다음 URL에서 접근할 수 있습니다:
- API 문서: http://localhost:8000/docs
- 서버 정보: http://localhost:8000
- 헬스 체크: http://localhost:8000/health

## API 엔드포인트

### 1. 이미지 업로드 OCR (`POST /ocr/upload`)

이미지 파일을 업로드하여 OCR 처리합니다.

**요청:**
- Content-Type: `multipart/form-data`
- Parameters:
  - `file`: 이미지 파일 (필수)
  - `include_bbox`: 바운딩 박스 정보 포함 여부 (선택, 기본값: false)

**응답 예제:**
```json
{
  "success": true,
  "filename": "test.jpg",
  "file_size": 123456,
  "processing_time": 2.345,
  "message": "텍스트 추출이 완료되었습니다",
  "text": "안녕하세요 반갑습니다",
  "word_count": 2,
  "character_count": 10,
  "words": [
    {
      "text": "안녕하세요",
      "confidence": 0.95,
      "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    },
    {
      "text": "반갑습니다",
      "confidence": 0.92,
      "bbox": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    }
  ]
}
```

### 2. 파일 경로 OCR (`POST /ocr/path`)

로컬 이미지 파일 경로를 사용하여 OCR 처리합니다.

**요청:**
- Content-Type: `application/x-www-form-urlencoded`
- Parameters:
  - `image_path`: 이미지 파일 경로 (필수)
  - `include_bbox`: 바운딩 박스 정보 포함 여부 (선택, 기본값: false)

**응답 예제:**
```json
{
  "success": true,
  "image_path": "/path/to/image.jpg",
  "file_size": 123456,
  "processing_time": 1.234,
  "message": "텍스트 추출이 완료되었습니다",
  "text": "한글 텍스트 인식 결과",
  "word_count": 3,
  "character_count": 12
}
```

### 3. 헬스 체크 (`GET /health`)

서버 상태를 확인합니다.

**응답 예제:**
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "ocr_service": "ready"
}
```

### 4. 서버 정보 (`GET /info`)

서버 정보를 조회합니다.

**응답 예제:**
```json
{
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
```

## 사용 예제

### Python 예제

```python
import requests

# 이미지 업로드 OCR
def ocr_upload(image_path):
    url = "http://localhost:8000/ocr/upload"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'include_bbox': True}
        response = requests.post(url, files=files, data=data)
    
    return response.json()

# 파일 경로 OCR
def ocr_path(image_path):
    url = "http://localhost:8000/ocr/path"
    data = {
        'image_path': image_path,
        'include_bbox': False
    }
    response = requests.post(url, data=data)
    return response.json()

# 사용 예제
result = ocr_upload("test.jpg")
print(f"추출된 텍스트: {result['text']}")
```

### cURL 예제

```bash
# 이미지 업로드 OCR
curl -X POST "http://localhost:8000/ocr/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.jpg" \
  -F "include_bbox=true"

# 파일 경로 OCR
curl -X POST "http://localhost:8000/ocr/path" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "image_path=/path/to/image.jpg&include_bbox=false"
```

## 지원 형식 및 제한사항

### 지원 이미지 형식
- JPG/JPEG
- PNG
- BMP
- TIFF/TIF

### 제한사항
- 최대 파일 크기: 10MB
- 언어: 한국어 (한글)
- OCR 엔진: PaddleOCR

## 에러 처리

### 일반적인 에러 응답

```json
{
  "success": false,
  "error": "에러 메시지",
  "message": "사용자 친화적 메시지"
}
```

### 주요 에러 코드
- `400`: 잘못된 요청 (파일 형식, 크기 등)
- `404`: 파일을 찾을 수 없음
- `500`: 서버 내부 오류

## 성능 최적화 팁

1. **이미지 품질**: 고해상도, 선명한 이미지 사용
2. **파일 크기**: 10MB 이하로 제한
3. **텍스트 방향**: 가로 방향 텍스트 권장
4. **배경**: 단순한 배경 사용
5. **폰트**: 명확한 폰트 사용 