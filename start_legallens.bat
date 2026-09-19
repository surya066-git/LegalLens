@echo off
echo =========================================
echo       Starting LegalLens AI App
echo =========================================

echo Starting Backend Server...
start "LegalLens Backend" cmd /k "cd services\api && call .venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "LegalLens Frontend" cmd /k "cd apps\web && npm run dev"

echo.
echo Servers have been launched in separate windows!
echo - Frontend: http://localhost:3000
echo - Backend:  http://127.0.0.1:8000
echo.
echo Press any key to exit this launcher...
pause > nul
