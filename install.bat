@echo off
REM Nautilus Installation Script for Windows
REM Uses an isolated virtual environment — mirrors install.sh behavior
setlocal enabledelayedexpansion

echo ====================================
echo   NAUTILUS Installation Script
echo ====================================
echo.

REM Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check for pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed. Please reinstall Python with pip.
    pause
    exit /b 1
)

echo [OK] pip found
echo.

REM ── Create isolated virtual environment ──
set "VENV_DIR=%LOCALAPPDATA%\nautilus-venv"

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Creating isolated environment at %VENV_DIR%...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo [OK] Virtual environment ready

REM Install package into the venv
echo Installing Python dependencies...
"%VENV_DIR%\Scripts\pip" install -e .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM ── Add a launcher shim to user PATH ──
set "BIN_DIR=%LOCALAPPDATA%\Microsoft\WindowsApps"
REM WindowsApps is already on PATH for most Windows installs; alternatively use %USERPROFILE%\.local\bin

REM Create a small wrapper script so 'nautilus' works from any terminal
set "SHIM=%VENV_DIR%\nautilus.cmd"
(
    echo @echo off
    echo "%VENV_DIR%\Scripts\python.exe" -m app %%*
) > "%SHIM%"

echo.
echo Checking optional dependencies...
echo.

REM Check for mpv
where mpv >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] mpv found
) else (
    echo [WARNING] mpv not found ^(required for playback^)
    echo    Download: https://mpv.io/installation/
    echo    Or install via: winget install mpv.mpv
)

REM Check for ffmpeg
where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] ffmpeg found
) else (
    echo [WARNING] ffmpeg not found ^(optional, for downloads^)
    echo    Download: https://ffmpeg.org/download.html
    echo    Or install via: winget install Gyan.FFmpeg
)

REM Check for yt-dlp
where yt-dlp >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] yt-dlp found
) else (
    echo [WARNING] yt-dlp not found ^(optional, for fast downloads^)
    echo    Install: pip install yt-dlp
)

REM Check for aria2c
where aria2c >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] aria2c found
) else (
    echo [INFO] aria2c not found ^(optional, for 10x faster downloads^)
    echo    Install via: winget install aria2.aria2
)

echo.
echo ====================================
echo   Installation complete!
echo ====================================
echo.
echo Virtual environment: %VENV_DIR%
echo.
echo To run Nautilus, use the venv directly:
echo   "%VENV_DIR%\Scripts\nautilus.exe"
echo.
echo Or add the venv Scripts folder to your PATH:
echo   set PATH=%VENV_DIR%\Scripts;%%PATH%%
echo.
echo Usage:
echo   nautilus                    # Start interactive search
echo   nautilus "Breaking Bad"     # Search directly
echo   nautilus -c                 # Continue watching
echo   nautilus -d                 # Download mode
echo.
echo Configuration is auto-detected:
echo   Platform default: %%APPDATA%%\nautilus\config.json
echo   Portable mode:    nautilus_config.json (next to project)
echo.
pause
