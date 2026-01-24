@echo off
echo Starting AI Chatbot Application...
echo.

REM Start Backend
echo [1/2] Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd /d "%~dp0" && python main.py"
timeout /t 3 /nobreak > nul

REM Start Frontend
echo [2/2] Starting React Frontend...
start "React Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo Application is starting!
echo ========================================
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to exit this window...
pause > nul
