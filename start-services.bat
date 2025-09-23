@echo off
echo ===================================
echo   Vietnamese AI Tutor - Local Setup
echo ===================================

echo.
echo [1/3] Starting Backend Service (FastAPI)...
start "Backend" cmd /k "cd /d %~dp0backend && .\venv\Scripts\activate && python main.py"
timeout /t 3 /nobreak >nul

echo [2/3] Starting AI Service (PhoGPT-4B)...
start "AI Service" cmd /k "cd /d %~dp0ai && .\venv\Scripts\activate && python app.py"
timeout /t 5 /nobreak >nul

echo [3/3] Starting Frontend (NextJS)...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===================================
echo Services are starting up...
echo ===================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo AI API:   http://localhost:5000
echo.
echo Press any key to close this window...
pause >nul