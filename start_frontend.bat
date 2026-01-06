@echo off
chcp 65001 > nul
title Telegram Bot Constructor - Frontend

echo ============================================
echo   Starting Frontend (React Dev Server)
echo ============================================
echo.

:: Check node_modules
if not exist "frontend\node_modules" (
    echo [WARNING] Node modules not found, installing...
    cd frontend
    call npm install
    cd ..
)

echo Starting React development server...
echo Frontend: http://localhost:3000
echo.
echo Press Ctrl+C to stop
echo.

cd frontend
call npm run dev

pause
