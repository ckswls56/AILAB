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

REM 실습 실행
echo 벡터 데이터베이스 실습을 실행합니다...
python vectordb_practice.py

pause 