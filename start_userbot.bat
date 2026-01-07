@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Telegram Userbot
echo   (Pyrogram)
echo ========================================
echo.

:: Проверяем виртуальное окружение
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

:: Проверяем .env файл
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

:: Создаём папку для логов
if not exist "logs" mkdir logs

:: Активируем виртуальное окружение
call venv\Scripts\activate.bat

echo Starting userbot...
echo Press Ctrl+C to stop
echo.

:: Запускаем userbot
python -m userbot.run

:: Деактивируем виртуальное окружение
call venv\Scripts\deactivate.bat

pause
