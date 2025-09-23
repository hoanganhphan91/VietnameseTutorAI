@echo off
echo ===================================
echo   Vietnamese AI Tutor - Clean Reset
echo ===================================

echo This will remove all installed dependencies and virtual environments.
set /p choice="Are you sure? (y/N): "
if /i not "%choice%"=="y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo 🧹 Cleaning up project...

REM Stop any running services first
echo Stopping any running services...
call stop-local.bat

REM Clean backend
echo Cleaning backend...
cd backend
if exist venv (
    echo Removing backend virtual environment...
    rmdir /s /q venv
)
cd ..

REM Clean AI service
echo Cleaning AI service...
cd ai
if exist venv (
    echo Removing AI virtual environment...
    rmdir /s /q venv
)
cd ..

REM Clean frontend
echo Cleaning frontend...
cd frontend
if exist node_modules (
    echo Removing node_modules...
    rmdir /s /q node_modules
)
if exist package-lock.json (
    echo Removing package-lock.json...
    del package-lock.json
)
cd ..

REM Clean other temp files
echo Cleaning temporary files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /d /r . %%d in (.next) do @if exist "%%d" rd /s /q "%%d"

echo.
echo ===================================
echo ✅ Project cleaned successfully!
echo ===================================
echo.
echo Now run: deploy-local.bat to reinstall everything
pause