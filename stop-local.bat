@echo off
echo 🛑 Stopping AI Vietnamese Tutor services...

echo Killing Python processes (Backend & AI)...
taskkill /f /im python.exe >nul 2>&1

echo Killing Node.js processes (Frontend)...
taskkill /f /im node.exe >nul 2>&1

echo Killing cmd processes...
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq AI Service*" ^| findstr cmd.exe') do taskkill /f /pid %%i >nul 2>&1
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq Backend API*" ^| findstr cmd.exe') do taskkill /f /pid %%i >nul 2>&1  
for /f "tokens=2" %%i in ('tasklist /fi "windowtitle eq Frontend*" ^| findstr cmd.exe') do taskkill /f /pid %%i >nul 2>&1

echo ✅ All services stopped!
echo.
pause