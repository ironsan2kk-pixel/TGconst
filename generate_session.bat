@echo off
chcp 65001 > nul
title Telegram Bot Constructor - Generate Pyrogram Session

echo ============================================
echo   Generate Pyrogram Session String
echo ============================================
echo.
echo This script will help you generate a session
echo string for the Pyrogram userbot.
echo.
echo You will need:
echo   1. API_ID from https://my.telegram.org
echo   2. API_HASH from https://my.telegram.org
echo   3. Your phone number
echo   4. Verification code from Telegram
echo.
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

:: Run session generator
python scripts\generate_session.py

echo.
echo ============================================
echo   Done!
echo ============================================
echo.
echo Copy the session string to your .env file:
echo USERBOT_SESSION_STRING=your_session_string_here
echo.
pause
