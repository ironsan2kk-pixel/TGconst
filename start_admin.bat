@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Запуск Admin Panel (Backend)
echo ========================================
echo.

:: Активация виртуального окружения
if not exist "venv\Scripts\activate.bat" (
    echo [ОШИБКА] Виртуальное окружение не найдено!
    echo Сначала запустите install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

:: Проверка .env
if not exist ".env" (
    echo [ОШИБКА] Файл .env не найден!
    echo Скопируйте .env.example в .env и настройте
    pause
    exit /b 1
)

echo Запуск FastAPI на http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo Health: http://localhost:8000/health
echo.
echo Для остановки нажмите Ctrl+C
echo.

python -m admin.run

:: Если вышли с ошибкой - показать
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сервер упал с ошибкой!
    pause
)
