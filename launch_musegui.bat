@echo off
REM MuseGUI Launcher Script for Windows
REM
REM Usage: Double-click this file or run from command prompt

REM Get script directory
set SCRIPT_DIR=%~dp0

REM Change to project directory
cd /d "%SCRIPT_DIR%"

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Launch MuseGUI
echo Starting MuseGUI...
python -m musegui.main

REM Pause if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Error occurred. Press any key to exit...
    pause > nul
)
