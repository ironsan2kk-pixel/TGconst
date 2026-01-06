@echo off
chcp 65001 > nul
title Telegram Bot Constructor - Build Frontend

echo ============================================
echo   Building Frontend for Production
echo ============================================
echo.

:: Check node_modules
if not exist "frontend\node_modules" (
    echo Installing dependencies first...
    cd frontend
    call npm install
    cd ..
)

echo Building React application...
echo.

cd frontend
call npm run build

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ============================================
echo   Build completed!
echo ============================================
echo.
echo Production files are in: frontend\dist
echo.
echo For deployment, copy the dist folder to your
echo web server or configure nginx to serve it.
echo.
pause
