@echo off
echo 벡터 데이터베이스 실습을 시작합니다...
echo.

REM 의존성 설치
echo 의존성 패키지를 설치합니다...
pip install -r requirements_vectordb.txt

echo.
echo PostgreSQL이 실행 중인지 확인하세요 (docker-compose up -d)
echo OpenAI API 키를 .env 파일에 설정하세요
echo.

echo.
echo 1. 데이터베이스 초기화 (기존 테이블 삭제 후 재생성)
echo 2. 벡터 데이터베이스 실습 실행
echo 3. 대화형 데모 실행
echo.

set /p choice="선택하세요 (1-3): "

if "%choice%"=="1" (
    echo 데이터베이스를 초기화합니다...
    python reset_database.py
) else if "%choice%"=="2" (
    echo 벡터 데이터베이스 실습을 실행합니다...
    python vectordb_practice.py
) else if "%choice%"=="3" (
    echo 대화형 데모를 실행합니다...
    python vectordb_demo.py
) else (
    echo 잘못된 선택입니다.
)

pause 