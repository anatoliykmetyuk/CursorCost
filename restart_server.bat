@echo off
REM Restart script for Windows to restart the Bokeh Cost Analysis Dashboard

echo Stopping any processes using port 5006...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5006 ^| findstr LISTENING') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo Creating virtual environment if it doesn't exist...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if not exist "venv\Scripts\python.exe" (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo Ensuring pip is available...
    venv\Scripts\python.exe -m ensurepip --upgrade
)

if not exist "venv\Scripts\python.exe" (
    echo ERROR: Python executable not found in virtual environment!
    pause
    exit /b 1
)

echo Upgrading pip...
venv\Scripts\python.exe -m ensurepip --upgrade
venv\Scripts\python.exe -m pip install --upgrade pip

if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found!
    pause
    exit /b 1
)

echo Installing/upgrading dependencies...
venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt

echo Starting Bokeh server on port 5006...
start "Bokeh Server" cmd /k "venv\Scripts\python.exe -m bokeh serve app.py --port 5006"

echo Waiting for server to initialize...
timeout /t 3 /nobreak >nul

echo Opening browser...
start http://localhost:5006/app

echo Server started! Dashboard should open in your browser.
pause

