@echo off
title Karasu Image Optimizer Manager
color 0B

:menu
cls
echo =======================================================
echo              Karasu Image Optimizer Manager
echo =======================================================
echo.
echo   [1] Start Application (DB, Backend, Frontend)
echo   [2] Stop Application (Shutdown all services)
echo   [3] Restart Application
echo   [4] Exit
echo.
echo =======================================================
echo.
set /p opt="Select an option (1-4): "

if "%opt%"=="1" goto start_app
if "%opt%"=="2" goto stop_app
if "%opt%"=="3" goto restart_app
if "%opt%"=="4" goto exit_mgr
goto menu

:start_app
cls
echo Starting Karasu Image Optimizer...
echo.

echo [1/4] Checking and starting PostgreSQL Database...
netstat -ano | findstr :5432 >nul
if %errorlevel% equ 0 (
    echo PostgreSQL is already running on port 5432.
) else (
    echo PostgreSQL is not running. Attempting to start PostgreSQL container...
    docker compose up -d postgres
    if %errorlevel% equ 0 (
        echo Started PostgreSQL container in background.
        echo Waiting 3 seconds for database to initialize...
        timeout /t 3 >nul
    ) else (
        echo WARNING: Could not start PostgreSQL database.
        echo The application will run in In-Memory fallback mode.
        timeout /t 2 >nul
    )
)

echo.
echo [2/4] Starting Flask Backend Server...
netstat -ano | findstr :5001 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo Port 5001 is already in use. Skipping start.
) else (
    start "Karasu Image Optimizer Backend" cmd /k "title Karasu Image Optimizer Backend && .venv\Scripts\python.exe -m backend.app"
)

echo.
echo [3/4] Starting Vite React Frontend Server...
netstat -ano | findstr :5173 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo Port 5173 is already in use. Skipping start.
) else (
    start "Karasu Image Optimizer Frontend" cmd /k "title Karasu Image Optimizer Frontend && cd frontend && npm run dev -- --host 127.0.0.1"
)

echo.
echo [4/4] Opening browser in 3 seconds...
timeout /t 3 >nul
start http://127.0.0.1:5173

echo.
echo Application started successfully!
pause
goto menu

:stop_app
cls
echo Stopping Karasu Image Optimizer...
echo.

echo [1/3] Stopping Frontend Server (Port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>nul
)
taskkill /f /t /fi "windowtitle eq Karasu Image Optimizer Frontend" >nul 2>nul

echo [2/3] Stopping Backend Server (Port 5001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>nul
)
taskkill /f /t /fi "windowtitle eq Karasu Image Optimizer Backend" >nul 2>nul

echo [3/3] Stopping PostgreSQL Database...
docker compose down >nul 2>nul
if %errorlevel% equ 0 (
    echo Stopped PostgreSQL container and freed resources.
) else (
    echo PostgreSQL container was not active.
)

echo.
echo All services stopped successfully!
pause
goto menu

:restart_app
cls
echo Restarting Karasu Image Optimizer...
echo.

echo [1/2] Stopping active services...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>nul
taskkill /f /fi "windowtitle eq Karasu Image Optimizer Frontend" >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001 ^| findstr LISTENING') do taskkill /f /pid %%a >nul 2>nul
taskkill /f /fi "windowtitle eq Karasu Image Optimizer Backend" >nul 2>nul
docker compose down >nul 2>nul
echo Active services stopped.
timeout /t 2 >nul

echo [2/2] Starting all services...
goto start_app

:exit_mgr
exit
