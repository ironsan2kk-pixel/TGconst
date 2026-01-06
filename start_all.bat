@echo off
chcp 65001 > nul
title Telegram Bot Constructor - Start All

echo ============================================
echo   Starting All Components
echo ============================================
echo.

:: Check venv
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

:: Check .env
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure it
    pause
    exit /b 1
)

echo Starting Backend...
start "Backend - FastAPI" cmd /k "call start_backend.bat"
timeout /t 3 > nul

echo Starting Userbot...
start "Userbot - Pyrogram" cmd /k "call start_userbot.bat"
timeout /t 2 > nul

echo Starting Frontend...
start "Frontend - React" cmd /k "call start_frontend.bat"

echo.
echo ============================================
echo   All components started!
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo Each component runs in a separate window.
echo Close this window or press any key to exit.
echo.
pause
