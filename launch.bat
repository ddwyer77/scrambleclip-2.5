@echo off
title Scramble Clip 2 by ClipmodeGo
color 0A

echo Scramble Clip 2 Launcher
echo Created by ClipmodeGo
echo.

:: Change to the directory where the batch file is located
cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Launch the application
echo Starting Scramble Clip 2...
python main.py

:: If the application crashes, keep the console window open
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Scramble Clip 2 crashed with error code %ERRORLEVEL%.
    echo.
    pause
) 