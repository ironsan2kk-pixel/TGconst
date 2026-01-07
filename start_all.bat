@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ════════════════════════════════════════════
echo   Telegram Channel Bot - Start All
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

echo 🚀 Starting all services in separate windows...
echo.

:: Start Admin API in new window
start "Admin API" cmd /k "cd /d "%~dp0" && call venv\Scripts\activate.bat && python -m admin.run"
echo ✅ Admin API started

:: Wait a bit
timeout /t 2 /nobreak > nul

:: Start Bot in new window
start "Telegram Bot" cmd /k "cd /d "%~dp0" && call venv\Scripts\activate.bat && python -m bot.run"
echo ✅ Telegram Bot started

echo.
echo ════════════════════════════════════════════
echo   All services started!
echo ════════════════════════════════════════════
echo.
echo Admin API: http://localhost:8000
echo API Docs:  http://localhost:8000/docs
echo.
echo Close this window or press any key to exit.
pause > nul
