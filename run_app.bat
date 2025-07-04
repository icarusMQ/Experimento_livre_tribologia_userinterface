@echo off
echo Starting Tribology Experiment User Interface...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7 or later and try again.
    pause
    exit /b 1
)

REM Check if requirements are installed
python -c "import serial, matplotlib, pandas" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
)

REM Run the application
python UI_experimento_livre_main.py

REM Pause if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
