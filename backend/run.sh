#!/bin/bash

# Shell script to run the FastAPI backend on Linux/Mac

echo "========================================"
echo "Kasparo Backend API - Starting Server"
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the server
echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo "Documentation available at http://localhost:8000/docs"
echo ""
python main.py
