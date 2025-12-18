#!/bin/bash
# Restart script for Unix/Linux/Mac to restart the Bokeh Cost Analysis Dashboard

echo "Stopping any processes using port 5006..."
# Try to find and kill processes on port 5006
if command -v lsof >/dev/null 2>&1; then
    lsof -ti:5006 | xargs kill -9 >/dev/null 2>&1
elif command -v fuser >/dev/null 2>&1; then
    fuser -k 5006/tcp >/dev/null 2>&1
else
    echo "Warning: Could not find lsof or fuser. Please manually stop processes on port 5006."
fi

sleep 2

echo "Creating virtual environment if it doesn't exist..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ ! -f "venv/bin/python" ]; then
        echo "ERROR: Failed to create virtual environment!"
        exit 1
    fi
    echo "Ensuring pip is available..."
    venv/bin/python -m ensurepip --upgrade
fi

if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment activation script not found!"
    echo "Recreating virtual environment..."
    rm -rf venv
    python3 -m venv venv
    if [ ! -f "venv/bin/python" ]; then
        echo "ERROR: Failed to create virtual environment!"
        exit 1
    fi
    venv/bin/python -m ensurepip --upgrade
fi

echo "Activating virtual environment..."
source venv/bin/activate

if [ ! -f "venv/bin/python" ]; then
    echo "ERROR: Python executable not found in virtual environment!"
    exit 1
fi

echo "Upgrading pip..."
venv/bin/python -m ensurepip --upgrade
venv/bin/python -m pip install --upgrade pip

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found!"
    exit 1
fi

echo "Installing/upgrading dependencies..."
venv/bin/python -m pip install --upgrade -r requirements.txt

if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found!"
    exit 1
fi

echo "Starting Bokeh server on port 5006..."
venv/bin/python -m bokeh serve app.py --port 5006 >/dev/null 2>&1 &
SERVER_PID=$!

echo "Waiting for server to initialize..."
sleep 3

echo "Opening browser..."
# Detect OS and open browser accordingly
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:5006/app
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open http://localhost:5006/app
    else
        echo "Please open http://localhost:5006/app in your browser"
    fi
else
    # Other Unix-like systems
    echo "Please open http://localhost:5006/app in your browser"
fi

echo "Server started! Dashboard should open in your browser."
echo "Server PID: $SERVER_PID"
echo "To stop the server, run: kill $SERVER_PID"

