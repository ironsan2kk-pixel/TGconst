@echo off
chcp 65001 > nul
title Telegram Bot Constructor - Stop All

echo ============================================
echo   Stopping All Components
echo ============================================
echo.

echo Stopping Python processes...
taskkill /F /IM python.exe /T 2>nul
if errorlevel 1 (
    echo No Python processes found
) else (
    echo Python processes stopped
)

echo.
echo Stopping Node processes...
taskkill /F /IM node.exe /T 2>nul
if errorlevel 1 (
    echo No Node processes found
) else (
    echo Node processes stopped
)

echo.
echo ============================================
echo   All components stopped!
echo ============================================
echo.
pause
