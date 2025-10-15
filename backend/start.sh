#!/bin/bash

echo "Starting TEX-SARTHI Backend Server..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo
echo "Starting Flask server..."
echo "Server will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop the server"
echo
python run.py
