@echo off
title Karasu Image Optimizer - Stopping Services
color 0C
echo =======================================================
echo          Stopping Karasu Image Optimizer Services
echo =======================================================
echo.

echo [1/3] Stopping Frontend Server (Port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>nul
)
taskkill /f /t /fi "windowtitle eq Karasu Image Optimizer Frontend" >nul 2>nul
echo Frontend server stopped and CMD window closed.

echo [2/3] Stopping Backend Server (Port 5001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>nul
)
taskkill /f /t /fi "windowtitle eq Karasu Image Optimizer Backend" >nul 2>nul
echo Backend server stopped and CMD window closed.

echo [3/3] Stopping PostgreSQL Database...
docker compose down >nul 2>nul
if %errorlevel% equ 0 (
    echo Stopped PostgreSQL container and freed resources.
) else (
    echo PostgreSQL container was not active.
)

echo.
echo =======================================================
echo All services and their CMD windows have been closed!
echo =======================================================
timeout /t 3
exit
