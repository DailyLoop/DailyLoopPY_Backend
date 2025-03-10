#!/bin/bash
set -e

echo "Starting NewsFeast services..."

# Start polling worker in the background
echo "Starting polling worker..."
python -m backend.microservices.polling_worker &

# Start API gateway in the foreground
echo "Starting API gateway..."
exec python backend/api_gateway/api_gateway.py