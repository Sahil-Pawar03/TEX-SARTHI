@echo off
echo Starting TEX-SARTHI Frontend Server...
echo =====================================
cd /d "%~dp0"
echo Serving from: %CD%
echo.
python -m http.server 8080
pause