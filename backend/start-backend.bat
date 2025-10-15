@echo off
echo Starting TEX-SARTHI Backend Server...
echo ====================================
cd /d "%~dp0"
call venv\Scripts\activate.bat
echo Backend starting on port 3000...
python run.py
pause