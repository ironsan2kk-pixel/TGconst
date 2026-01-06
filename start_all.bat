@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Запуск всех компонентов
echo ========================================
echo.

:: Проверка .env
if not exist ".env" (
    echo [ОШИБКА] Файл .env не найден!
    echo Скопируйте .env.example в .env и заполните
    pause
    exit /b 1
)

echo [INFO] Запуск Admin Backend (FastAPI)...
start "Admin Backend" cmd /k "call start_admin.bat"
timeout /t 3 >nul

echo [INFO] Запуск Telegram Bot...
start "Telegram Bot" cmd /k "call start_bot.bat"
timeout /t 2 >nul

echo [INFO] Запуск Userbot (Pyrogram)...
start "Userbot" cmd /k "call start_userbot.bat"
timeout /t 2 >nul

echo [INFO] Запуск Frontend (React)...
start "Frontend" cmd /k "call start_frontend.bat"

echo.
echo ========================================
echo   Все компоненты запущены!
echo ========================================
echo.
echo   Admin Backend: http://localhost:8000
echo   Frontend:      http://localhost:3000
echo   API Docs:      http://localhost:8000/docs
echo.
echo   Для остановки запустите stop_all.bat
echo ========================================
echo.

pause
