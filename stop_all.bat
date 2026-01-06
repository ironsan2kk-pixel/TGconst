@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   Остановка всех компонентов
echo ========================================
echo.

echo [INFO] Остановка Python процессов...
taskkill /f /im python.exe 2>nul
if %errorlevel% equ 0 (
    echo [OK] Python процессы остановлены
) else (
    echo [INFO] Python процессы не найдены
)

echo.
echo [INFO] Остановка Node.js процессов...
taskkill /f /im node.exe 2>nul
if %errorlevel% equ 0 (
    echo [OK] Node.js процессы остановлены
) else (
    echo [INFO] Node.js процессы не найдены
)

echo.
echo [INFO] Закрытие окон командной строки...
:: Закрываем окна с определёнными заголовками
taskkill /fi "WINDOWTITLE eq Admin Backend*" 2>nul
taskkill /fi "WINDOWTITLE eq Telegram Bot*" 2>nul
taskkill /fi "WINDOWTITLE eq Userbot*" 2>nul
taskkill /fi "WINDOWTITLE eq Frontend*" 2>nul

echo.
echo ========================================
echo   Все компоненты остановлены!
echo ========================================
echo.

pause
