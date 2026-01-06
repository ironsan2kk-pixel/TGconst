@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Generate Pyrogram Session String
echo ========================================
echo.

:: Проверяем виртуальное окружение
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

:: Активируем виртуальное окружение
call venv\Scripts\activate.bat

:: Запускаем скрипт генерации
python scripts\generate_session.py

:: Деактивируем виртуальное окружение
call venv\Scripts\deactivate.bat

pause
