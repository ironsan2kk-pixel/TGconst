@echo off
chcp 65001 > nul
title Telegram Bot Constructor - Create Admin

echo ============================================
echo   Create Admin User
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

:: Run admin creator
python scripts\create_admin.py

echo.
pause
