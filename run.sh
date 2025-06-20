#!/bin/bash

# Script to run the Invoice to Order Processing System

# Make sure script is executable
# chmod +x run.sh

# Create necessary directories
mkdir -p app/uploads app/processed

# Check if running in simple mode or full mode
if [ "$1" == "simple" ]; then
    echo "Starting simple test server on http://localhost:8080"
    python3 app.py
else
    echo "Starting full application on http://localhost:8000"
    python3 main.py
fi 