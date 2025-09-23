@echo off
echo ===================================
echo   Vietnamese AI Tutor - Service Status
echo ===================================

echo.
echo Checking service endpoints...
echo.

echo [Frontend] http://localhost:3000
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:3000 2>nul || echo Status: Not responding

echo [Backend API] http://localhost:8000/docs
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:8000/docs 2>nul || echo Status: Not responding

echo [AI Service] http://localhost:5000/health
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:5000/health 2>nul || echo Status: Not responding

echo.
echo ===================================
echo.
echo Press any key to close...
pause >nul