@echo off
REM ============================================================================
REM  OpenGPT - Windows startup script
REM  Starts the FastAPI backend (port 8000) and the React frontend (port 3000).
REM ============================================================================

setlocal
set ROOT=%~dp0
set BACKEND=%ROOT%backend
set FRONTEND=%ROOT%frontend
set VENV=%ROOT%.venv

REM --- Start Backend ---------------------------------------------------------
if exist "%VENV%\Scripts\activate.bat" (
    start "Backend" cmd /k "call %VENV%\Scripts\activate.bat && cd /d %BACKEND% && python main.py"
) else (
    start "Backend" cmd /k "cd /d %BACKEND% && python main.py"
)

REM --- Start Frontend --------------------------------------------------------
start "Frontend" cmd /k "cd /d %FRONTEND% && npm install && npm run dev"

echo.
echo Starting backend (http://localhost:8000) and frontend (http://localhost:3000)...
echo Close the opened terminal windows to stop the servers.
endlocal
