#!/bin/bash

# AI Fraud Detection API - Server Startup Script

echo "Starting AI Fraud Detection API..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
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

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p models
mkdir -p temp_uploads
mkdir -p logs

# Set environment variables
export PYTHONPATH=$(pwd)
export FLASK_APP=app.py
export FLASK_ENV=production

# Start the server
echo "Starting server on http://localhost:5000"
echo "API Documentation: http://localhost:5000/api/v1/health"
echo "Use API Key: sandbox_key_12345"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py