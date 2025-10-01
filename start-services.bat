@echo off
echo ===================================
echo   Vietnamese AI Tutor - Start Services
echo ===================================

REM Check if port 8000 is in use
netstat -an | find "LISTENING" | find ":8000" >nul
if not errorlevel 1 (
    echo ❌ Port 8000 is already in use!
    echo Please run stop-local.bat first or kill the process
    pause
    exit /b 1
)

echo.
echo [1/3] Starting Backend Service (FastAPI)...
cd /d %~dp0backend
if not exist venv (
    echo ❌ Virtual environment not found! Please run deploy-local.bat first
    pause
    exit /b 1
)
start "Vietnamese Tutor - Backend" cmd /k "call venv\Scripts\activate.bat && echo Backend starting on port 8000... && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 5 /nobreak >nul


echo [2/3] Starting Rasa Chatbot Service...
cd /d %~dp0rasa
if not exist .venv (
    echo ❌ Virtual environment for Rasa not found! Please run deploy-local.bat first
    pause
    exit /b 1
)
start "Vietnamese Tutor - Rasa Chatbot" cmd /k "call .venv\Scripts\activate.bat && echo Rasa Chatbot starting on port 5005... && rasa run --enable-api --cors '*' --debug"
timeout /t 3 /nobreak >nul

echo [3/3] Starting Frontend (NextJS)...
cd /d %~dp0frontend
if not exist node_modules (
    echo ❌ Node modules not found! Please run deploy-local.bat first
    pause
    exit /b 1
)

REM Create environment file

echo Creating environment configuration...
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
echo NEXT_PUBLIC_AI_URL=http://localhost:5005 >> .env.local
start "Vietnamese Tutor - Frontend" cmd /k "echo Frontend starting on port 3000... && npm run dev"

echo.
echo ===================================
echo Services are starting up...
echo ===================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8000
echo 🤖 AI API:   http://localhost:5005 (Rasa Chatbot)
echo.
echo To stop all services: stop-local.bat
echo.
echo Waiting for services to start...
timeout /t 15 /nobreak >nul

echo Checking services...
curl -s http://localhost:8000 >nul && echo ✅ Backend is running || echo ❌ Backend failed
curl -s http://localhost:5005 >nul && echo ✅ Rasa Chatbot is running || echo ❌ Rasa Chatbot failed
curl -s http://localhost:3000 >nul && echo ✅ Frontend is running || echo ❌ Frontend failed

echo.
echo Press any key to close this window...
pause >nul