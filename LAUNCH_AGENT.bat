@echo off
setlocal enabledelayedexpansion
title AI Resume & Portfolio Builder Agent - Special Launcher
color 0B
cls

echo.
echo  ====================================================================
echo    * AI RESUME & PORTFOLIO BUILDER AGENT - LAUNCH CONTROL *
echo  ====================================================================
echo.
echo   [1] Instant Launch Dashboard (Zero Server Error - 100% Reliable)
echo   [2] Launch with High-Speed Local Python Web Server
echo   [3] Create Instant 1-Click Desktop Shortcut
echo   [4] Open Dashboard Folder in Windows Explorer
echo   [5] Exit
echo.
echo  ====================================================================
set /p choice="  Choose option (Press 1, 2, 3, 4, 5 or Enter for [1]): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto launch_direct
if "%choice%"=="2" goto launch_server
if "%choice%"=="3" goto make_shortcut
if "%choice%"=="4" goto open_folder
if "%choice%"=="5" goto end

:launch_direct
echo.
echo  [+] Launching AI Agent Dashboard directly in your default browser...
start "" "%~dp0index.html"
echo  [OK] Dashboard is now OPEN!
timeout /t 2 >nul
goto end

:launch_server
echo.
echo  [+] Starting Python Agent Server...
python "%~dp0launch.py" --server
if %ERRORLEVEL% NEQ 0 (
    echo [!] Python not available in path, switching to direct mode...
    start "" "%~dp0index.html"
)
goto end

:make_shortcut
echo.
echo  [+] Creating Desktop Shortcut...
powershell -ExecutionPolicy Bypass -File "%~dp0create_shortcut.ps1"
echo.
pause
goto end

:open_folder
start "" "%~dp0"
goto end

:end
exit
