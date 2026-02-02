@echo off
REM Nautilus Installation Script for Windows
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
where pip >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not installed. Please reinstall Python with pip.
    pause
    exit /b 1
)

echo [OK] pip found
echo.

REM Install package in editable mode
echo Installing Python dependencies...
pip install -e .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

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
echo Usage:
echo   nautilus                    # Start interactive search
echo   nautilus "Breaking Bad"     # Search directly
echo   nautilus -c                 # Continue watching
echo   nautilus -d                 # Download mode
echo.
echo Configuration: %%APPDATA%%\nautilus\config.yaml
echo.
pause
