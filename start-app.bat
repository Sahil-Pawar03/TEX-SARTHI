@echo off
echo Starting TEX-SARTHI Application...
echo =====================================

echo Starting Backend Server (Port 3000)...
cd backend
start "TEX-SARTHI Backend" cmd /k "call start-backend.bat"

echo Waiting for backend to start...
timeout /t 5 /nobreak

echo Starting Frontend Server (Port 8080)...
cd ..\frontend
start "TEX-SARTHI Frontend" cmd /k "call start-frontend.bat"

echo.
echo Waiting for frontend to start...
timeout /t 3 /nobreak

echo.
echo =====================================
echo TEX-SARTHI Application Started!
echo.
echo Backend API: http://localhost:3000
echo Frontend Web: http://localhost:8080
echo.
echo Default Admin Login:
echo Email: admin@texsarthi.com
echo Password: admin123
echo.
echo Opening web browser...
start http://localhost:8080
echo.
echo Press any key to close this window...
pause > nul
