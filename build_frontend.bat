@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Сборка Frontend (Production Build)
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
echo [INFO] Запуск сборки...
call npm run build

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Сборка завершена успешно!
    echo ========================================
    echo.
    echo   Результат в папке: frontend/dist/
    echo.
    echo   Для деплоя скопируйте содержимое
    echo   папки dist на ваш веб-сервер.
    echo.
) else (
    echo.
    echo [ОШИБКА] Сборка завершилась с ошибкой!
)

pause
