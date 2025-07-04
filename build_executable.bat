@echo off
echo Building Tribology Experiment Standalone Executable...
echo.

REM Check if Python and PyInstaller are available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7 or later and try again.
    pause
    exit /b 1
)

REM Install requirements if not already installed
echo Installing/updating requirements...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM Build the executable
echo Building executable with PyInstaller...
python -m PyInstaller tribology_experiment.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable is located at: dist\TribologyExperiment.exe
echo.

REM Ask if user wants to run the executable
set /p run_exe="Do you want to run the executable now? (y/n): "
if /i "%run_exe%"=="y" (
    echo Running executable...
    start "" "dist\TribologyExperiment.exe"
)

pause
