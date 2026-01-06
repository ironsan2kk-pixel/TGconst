@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Запуск Telegram бота
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ОШИБКА] Виртуальное окружение не найдено!
    echo Сначала запустите install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo [INFO] Запуск бота...
echo.

python -m bot.run

echo.
echo [INFO] Бот остановлен
pause
