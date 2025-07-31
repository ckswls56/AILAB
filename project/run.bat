@echo off
echo PaddleOCR 한글 이미지 인식 AI 서버를 시작합니다...
echo.

REM Python 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
)

REM 의존성 설치 확인
echo 의존성을 확인합니다...
pip install -r requirements.txt

echo.
echo 서버를 시작합니다...
echo API 문서: http://localhost:8000/docs
echo 서버 주소: http://localhost:8000
echo.

python main.py

pause 