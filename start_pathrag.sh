#!/bin/bash

# PathRAG API Startup Script
# This script starts the PathRAG API server on port 5000

# Set working directory
cd /opt/pathrag/pathrag

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="/opt/pathrag/pathrag:$PYTHONPATH"
export FLASK_PORT=5000

# Start the API server
echo "Starting PathRAG API server on port 5000..."
python src/api_server_simple.py
