@echo off
REM Streamlit 프론트엔드 실행
cd /d %~dp0
cd frontend
streamlit run app.py 