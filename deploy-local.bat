@echo off
echo 🚀 Setting up AI Vietnamese Tutor (Local Development)...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ first
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js first
    pause
    exit /b 1
)

echo ✅ Python and Node.js found

REM Create virtual environment for backend
echo 📦 Setting up Python virtual environment...
if not exist backend\venv (
    cd backend
    python -m venv venv
    cd ..
)

REM Activate virtual environment and install dependencies
echo 📥 Installing Python dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

REM Install frontend dependencies
echo 📥 Installing Node.js dependencies...
cd frontend
npm install
cd ..

REM Install AI dependencies
echo 📥 Installing AI dependencies...
cd ai
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
cd ..

REM Create local config files
echo ⚙️ Creating local configuration...

REM Backend environment
echo DATABASE_URL=sqlite:///./vietnamese_tutor.db > backend\.env
echo REDIS_URL=redis://localhost:6379 >> backend\.env
echo AI_SERVICE_URL=http://localhost:5000 >> backend\.env

REM Add email validator to backend requirements
cd backend
call venv\Scripts\activate.bat
pip install pydantic[email]
cd ..

REM Frontend environment
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > frontend\.env.local
echo NEXT_PUBLIC_AI_URL=http://localhost:5000 >> frontend\.env.local

echo 🎯 Starting services...

REM Start AI service in background
echo 🤖 Starting AI service on port 5000...
start "AI Service" cmd /c "cd /d %cd%\ai && venv\Scripts\activate.bat && python app.py"

REM Wait a bit for AI service to start
timeout /t 10 /nobreak >nul

REM Start backend in background
echo 🔧 Starting FastAPI backend on port 8000...
start "Backend API" cmd /c "cd /d %cd%\backend && venv\Scripts\activate.bat && python create_sample_data.py && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

REM Wait a bit for backend to start
timeout /t 10 /nobreak >nul

REM Start frontend
echo 🌐 Starting NextJS frontend on port 3000...
start "Frontend" cmd /c "cd frontend && npm run dev"

echo ✅ All services started!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 🤖 AI Service: http://localhost:5000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 📝 To stop services: Close the command windows or press Ctrl+C in each
echo 🔄 To restart: Run this script again
echo.
pause