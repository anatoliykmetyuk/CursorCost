#!/bin/bash
# Startup script for Unix/Linux/Mac to run the Bokeh Cost Analysis Dashboard

echo "Creating virtual environment if it doesn't exist..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/upgrading dependencies..."
pip install --upgrade -r requirements.txt

echo "Starting Bokeh server..."
bokeh serve app.py --show

