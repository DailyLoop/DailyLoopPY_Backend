#!/bin/bash

# start-polling-worker.sh
# Script to start the polling worker for tracking news stories

echo "Starting News Aggregator Polling Worker..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
fi

# Install dependencies if needed
if [ "$1" == "--install" ]; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
fi

# Set environment variables from .env file if it exists
if [ -f ".env" ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
fi

# Start the polling worker
echo "Starting polling worker..."
python -m backend.microservices.polling_worker

# Keep this script running until manually terminated
echo "Polling worker started. Press Ctrl+C to stop."