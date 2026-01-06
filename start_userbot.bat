@echo off
chcp 65001 > nul
title Telegram Bot Constructor - Userbot

echo ============================================
echo   Starting Userbot (Pyrogram)
echo ============================================
echo.

:: Check venv
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

:: Activate venv
call venv\Scripts\activate.bat

:: Check .env
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure it
    pause
    exit /b 1
)

echo Starting Pyrogram userbot...
echo.
echo Press Ctrl+C to stop
echo.

python userbot\run.py

pause
