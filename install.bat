@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Установка Telegram Channel Bot
echo ========================================
echo.

:: Проверка Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден! Установите Python 3.11+
    pause
    exit /b 1
)

echo [1/5] Создание виртуального окружения...
if not exist "venv" (
    python -m venv venv
    echo       Виртуальное окружение создано
) else (
    echo       Виртуальное окружение уже существует
)

echo.
echo [2/5] Активация виртуального окружения...
call venv\Scripts\activate.bat

echo.
echo [3/5] Установка зависимостей...
pip install --upgrade pip > nul
pip install -r requirements.txt

echo.
echo [4/5] Настройка конфигурации...
if not exist ".env" (
    copy .env.example .env > nul
    echo       Создан файл .env - ОТРЕДАКТИРУЙТЕ ЕГО!
) else (
    echo       Файл .env уже существует
)

echo.
echo [5/5] Инициализация базы данных...
if not exist "data" mkdir data
if not exist "data\backups" mkdir data\backups
python scripts/setup_db.py

echo.
echo ========================================
echo   Установка завершена!
echo ========================================
echo.
echo Следующие шаги:
echo 1. Отредактируйте файл .env
echo 2. Запустите start_admin.bat
echo.

pause
