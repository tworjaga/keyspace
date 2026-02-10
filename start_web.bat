@echo off
REM Keyspace - Web Interface Startup Script

REM Change to script directory
cd /d "%~dp0"

echo.
echo     +-------------------------------------------+
echo     ^|                                           ^|
echo     ^|   K E Y S P A C E   -   Web Interface     ^|
echo     ^|                                           ^|
echo     +-------------------------------------------+

echo.
echo               Web Interface v1.0
echo.

echo Starting Keyspace Web Server...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/update requirements
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo.
echo Starting Web Server...
echo.

REM Start the web application
python web_app.py

REM Deactivate virtual environment
deactivate

pause
