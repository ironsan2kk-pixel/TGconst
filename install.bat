@echo off
chcp 65001 > nul
title Telegram Bot Constructor - Installation

echo ============================================
echo   Telegram Bot Constructor - Installation
echo ============================================
echo.

:: Check Python
echo [1/6] Checking Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

:: Check Node.js
echo [2/6] Checking Node.js...
node --version > nul 2>&1
if errorlevel 1 (
    echo [WARNING] Node.js not found. Install it for frontend.
    echo Download: https://nodejs.org/
) else (
    node --version
    echo [OK] Node.js found
)
echo.

:: Create virtual environment
echo [3/6] Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

:: Activate venv and install dependencies
echo [4/6] Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Python dependencies installed
echo.

:: Install Node.js dependencies
echo [5/6] Installing Node.js dependencies (frontend)...
if exist "frontend\package.json" (
    cd frontend
    call npm install
    cd ..
    echo [OK] Node.js dependencies installed
) else (
    echo [WARNING] frontend/package.json not found, skipping
)
echo.

:: Setup .env
echo [6/6] Setting up environment...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo [OK] .env file created from .env.example
        echo [WARNING] Please edit .env file with your settings!
    ) else (
        echo [WARNING] .env.example not found
    )
) else (
    echo [WARNING] .env file already exists
)
echo.

:: Create data directories
if not exist "data" mkdir data
if not exist "data\bots" mkdir data\bots
echo [OK] Data directories created
echo.

:: Create admin
echo Creating admin user...
python scripts\create_admin.py
echo.

echo ============================================
echo   Installation completed!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your settings
echo 2. Run: generate_session.bat (for Pyrogram)
echo 3. Run: start_backend.bat
echo 4. Run: start_userbot.bat
echo 5. Run: start_frontend.bat
echo.
echo Or run: start_all.bat
echo.
pause
