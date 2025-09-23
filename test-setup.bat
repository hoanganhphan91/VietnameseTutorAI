@echo off
echo ===================================
echo   Testing Vietnamese AI Tutor Setup
echo ===================================

echo.
echo [TEST 1] Checking Backend Dependencies...
cd /d %~dp0backend
call .\venv\Scripts\activate
python -c "import fastapi, sqlalchemy; print('✓ Backend dependencies OK')"
if errorlevel 1 (
    echo ✗ Backend dependencies failed
    pause
    exit /b 1
)

echo.
echo [TEST 2] Testing Database...
python -c "from database import engine; from sqlalchemy import text; conn = engine.connect(); print('✓ Database connection OK'); conn.close()"
if errorlevel 1 (
    echo ✗ Database connection failed
    pause
    exit /b 1
)

echo.
echo [TEST 3] Checking AI Dependencies...
cd /d %~dp0ai
call .\venv\Scripts\activate
python -c "import torch, transformers; print('✓ AI dependencies OK')"
if errorlevel 1 (
    echo ✗ AI dependencies failed
    pause
    exit /b 1
)

echo.
echo [TEST 4] Checking Frontend...
cd /d %~dp0frontend
call npm run build
if errorlevel 1 (
    echo ✗ Frontend build failed
    pause
    exit /b 1
)

echo.
echo ===================================
echo ✓ All tests passed! Ready to deploy.
echo ===================================
echo.
echo Run 'start-services.bat' to launch the app
pause