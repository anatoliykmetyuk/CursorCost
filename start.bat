@echo off
REM Startup script for Windows to run the Bokeh Cost Analysis Dashboard

echo Creating virtual environment if it doesn't exist...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/upgrading dependencies...
pip install --upgrade -r requirements.txt

echo Starting Bokeh server...
bokeh serve app.py --show

pause

