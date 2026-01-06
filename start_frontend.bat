@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Запуск Frontend (React Admin Panel)
echo ========================================
echo.

:: Проверка Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] Node.js не установлен!
    echo Скачайте с https://nodejs.org/
    pause
    exit /b 1
)

:: Переход в папку frontend
cd frontend

:: Проверка node_modules
if not exist "node_modules\" (
    echo [INFO] Установка зависимостей...
    call npm install
    if %errorlevel% neq 0 (
        echo [ОШИБКА] Не удалось установить зависимости
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Запуск dev сервера на http://localhost:3000
echo [INFO] Нажмите Ctrl+C для остановки
echo.

:: Запуск dev сервера
call npm run dev

pause
