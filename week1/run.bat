@echo off
echo ========================================
echo    3D Gomoku Game - AI Lab Week 1
echo ========================================
echo.

REM Python 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python이 설치되지 않았습니다.
    echo Python 3.8 이상을 설치해주세요.
    pause
    exit /b 1
)

echo [INFO] Python 버전 확인 완료
echo.

REM 가상환경 확인
if exist "venv\Scripts\activate.bat" (
    echo [INFO] 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
) else (
    echo [INFO] 가상환경이 없습니다. 시스템 Python을 사용합니다.
)

echo.

REM 의존성 설치 확인
echo [INFO] 필요한 라이브러리를 확인합니다...
python -c "import pygame, numpy" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 필요한 라이브러리를 설치합니다...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] 라이브러리 설치에 실패했습니다.
        pause
        exit /b 1
    )
) else (
    echo [INFO] 필요한 라이브러리가 이미 설치되어 있습니다.
)

echo.
echo [INFO] 게임을 시작합니다...
echo.

REM 게임 실행
python main.py

echo.
echo [INFO] 게임이 종료되었습니다.
pause 