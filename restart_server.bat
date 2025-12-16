@echo off
echo Stopping any processes using port 5006...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5006 ^| findstr LISTENING') do (
    echo Killing process %%a
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo Starting Bokeh server on port 5006...
start "Bokeh Server" cmd /k "python -m bokeh serve app.py --port 5006"
echo Server started! Open http://localhost:5006/app in your browser
pause

