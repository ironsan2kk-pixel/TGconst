@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ════════════════════════════════════════════
echo   Telegram Channel Bot - Bot
echo ════════════════════════════════════════════
echo.

:: Check venv
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Run install.bat first.
    pause
    exit /b 1
)

:: Check .env
if not exist ".env" (
    echo ❌ .env file not found!
    echo Copy .env.example to .env and configure it.
    pause
    exit /b 1
)

:: Activate venv
call venv\Scripts\activate.bat

:: Start bot
echo 🤖 Starting Telegram bot...
echo.
python -m bot.run

pause
