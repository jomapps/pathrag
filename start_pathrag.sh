#!/bin/bash

# PathRAG API Startup Script
# This script properly activates the virtual environment and starts the API server

# Set working directory
cd /opt/pathrag/pathrag

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export PYTHONPATH="/opt/pathrag/pathrag:$PYTHONPATH"

# Start the API server
python src/api_server_simple.py
