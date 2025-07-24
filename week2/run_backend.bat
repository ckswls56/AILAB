@echo off
REM FastAPI 백엔드 실행 (uvicorn)
cd /d %~dp0\..
set PYTHONPATH=%CD%
uvicorn week2.backend.main:app --reload --port 8000