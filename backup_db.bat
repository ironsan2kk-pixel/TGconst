@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo   🗄️ Database Backup Tool
echo ========================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo    Run install.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

if "%1"=="" (
    python scripts\backup_db.py create
) else (
    python scripts\backup_db.py %*
)

echo.
echo ========================================
echo   Commands:
echo   backup_db.bat           - Create backup
echo   backup_db.bat list      - List backups
echo   backup_db.bat cleanup 5 - Keep 5 latest
echo ========================================

pause
