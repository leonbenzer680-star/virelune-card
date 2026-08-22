@echo off
REM Personal AI Assistant - Setup Wizard Launcher
REM Just double-click this file to start setup!

echo.
echo ================================================
echo  Personal AI Assistant - Setup Wizard
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found
    echo Please install Python from: https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run setup wizard
echo.
echo Starting Setup Wizard...
echo.
python setup_wizard.py

pause
