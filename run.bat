@echo off
title ProfileAuditor Launcher
cls
echo ===================================================
echo           Starting ProfileAuditor Application
echo ===================================================
echo.

:: Get project root directory
set "ROOT_DIR=%~dp0"

echo [1/2] Starting Backend (FastAPI on Port 8000)...
start "ProfileAuditor - Backend" cmd /k "cd /d "%ROOT_DIR%backend" && (if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) else (echo No .venv found, using system Python...)) && python -m uvicorn app.main:app --reload --port 8000"

echo [2/2] Starting Frontend (React on Port 3000)...
start "ProfileAuditor - Frontend" cmd /k "cd /d "%ROOT_DIR%frontend" && npm start"

echo.
echo ===================================================
echo   ProfileAuditor is starting in separate windows!
echo   - Frontend:  http://localhost:3000
echo   - Backend:   http://localhost:8000
echo   - API Docs:  http://localhost:8000/docs
echo ===================================================
echo.
echo Keep the backend and frontend command windows open while using the app.
echo You can close this launcher window now.
pause
