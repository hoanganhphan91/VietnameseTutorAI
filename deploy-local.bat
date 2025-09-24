@echo off
echo ===================================
echo   Vietnamese AI Tutor - Full Setup
echo ===================================

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

REM Check if port 8000 is in use
netstat -an | find "LISTENING" | find ":8000" >nul
if not errorlevel 1 (
    echo ❌ Port 8000 is already in use!
    echo Please stop the process using port 8000 first
    pause
    exit /b 1
)

REM Setup Backend
echo [1/3] Setting up Backend (FastAPI)...
cd backend

REM Remove old virtual environment if exists
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

REM Create fresh virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
echo Installing/updating backend dependencies...
pip install --upgrade pip
pip install email-validator
pip install -r requirements.txt

REM Create sample data
if exist create_sample_data.py (
    echo Creating sample data...
    python create_sample_data.py || echo Warning: Sample data creation failed, continuing...
)

REM Create environment file
echo Creating backend environment configuration...
echo DATABASE_URL=sqlite:///./vietnamese_tutor.db > .env
echo AI_SERVICE_URL=http://localhost:5000 >> .env
echo REDIS_URL=redis://localhost:6379 >> .env
cd ..

REM Setup AI Service
echo [2/3] Setting up AI Service (PhoGPT-4B)...
cd ai

REM Remove old virtual environment if exists
if exist venv (
    echo Removing old AI virtual environment...
    rmdir /s /q venv
)

REM Create fresh virtual environment
echo Creating Python virtual environment for AI...
python -m venv venv

call venv\Scripts\activate.bat
echo Installing/updating AI dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Create models directory
if not exist "..\models" mkdir "..\models"
cd ..

REM Setup Frontend
echo [3/3] Setting up Frontend (NextJS)...
cd frontend

REM Remove old node_modules if exists
if exist node_modules (
    echo Removing old node_modules...
    rmdir /s /q node_modules
)

REM Install fresh node modules
echo Installing Node.js dependencies...
npm install

REM Create environment file
echo Creating environment configuration...
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
echo NEXT_PUBLIC_AI_URL=http://localhost:5000 >> .env.local
cd ..

echo.
echo ===================================
echo Setup completed successfully!
echo ===================================
echo.
echo To start all services, run: start-services.bat
echo To stop all services, run: stop-local.bat
echo.
pause
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