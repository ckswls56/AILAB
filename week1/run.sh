#!/bin/bash

echo "========================================"
echo "   3D Gomoku Game - AI Lab Week 1"
echo "========================================"
echo

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3가 설치되지 않았습니다."
    echo "Python 3.8 이상을 설치해주세요."
    exit 1
fi

echo "[INFO] Python 버전 확인 완료"
echo

# 가상환경 확인
if [ -f "venv/bin/activate" ]; then
    echo "[INFO] 가상환경을 활성화합니다..."
    source venv/bin/activate
else
    echo "[INFO] 가상환경이 없습니다. 시스템 Python을 사용합니다."
fi

echo

# 의존성 설치 확인
echo "[INFO] 필요한 라이브러리를 확인합니다..."
if ! python3 -c "import pygame, numpy" &> /dev/null; then
    echo "[INFO] 필요한 라이브러리를 설치합니다..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] 라이브러리 설치에 실패했습니다."
        exit 1
    fi
else
    echo "[INFO] 필요한 라이브러리가 이미 설치되어 있습니다."
fi

echo
echo "[INFO] 게임을 시작합니다..."
echo

# 게임 실행
python3 main.py

echo
echo "[INFO] 게임이 종료되었습니다." 