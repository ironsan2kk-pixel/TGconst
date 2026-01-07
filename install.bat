@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ════════════════════════════════════════════
echo   Telegram Channel Bot - Installation
echo ════════════════════════════════════════════
echo.

:: Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

:: Create virtual environment
echo 📦 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ℹ️ Virtual environment already exists
)
echo.

:: Activate venv and install packages
echo 📥 Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip > nul
pip install -r requirements.txt
echo ✅ Dependencies installed
echo.

:: Copy .env if not exists
if not exist ".env" (
    echo 📝 Creating .env file...
    copy .env.example .env > nul
    echo ✅ .env created from .env.example
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and fill in your credentials!
) else (
    echo ℹ️ .env file already exists
)
echo.

:: Create data directory
if not exist "data" (
    mkdir data
    mkdir data\backups
    echo ✅ Data directories created
)
echo.

:: Initialize database
echo 🔧 Initializing database...
python scripts\setup_db.py
echo.

echo ════════════════════════════════════════════
echo   ✅ Installation complete!
echo ════════════════════════════════════════════
echo.
echo Next steps:
echo   1. Edit .env file with your credentials
echo   2. Run start_all.bat to start the bot
echo.
pause
