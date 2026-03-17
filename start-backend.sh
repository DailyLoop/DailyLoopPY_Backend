#!/bin/bash

# ============================================================
# News Aggregator Backend - Start Script
# ============================================================
# This script starts the Flask API Gateway server for the
# News Aggregator Backend application.

set -e

echo "=========================================="
echo "Starting News Aggregator Backend"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and fill in the required values."
    exit 1
fi

# Check if required environment variables are set
required_vars=("SUPABASE_URL" "SUPABASE_SERVICE_ROLE_KEY" "SUPABASE_JWT_SECRET" "NEWS_API_KEY" "GEMINI_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep "^${var}=your-" .env > /dev/null; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Error: Missing or incomplete environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

echo "✓ Environment variables configured"

# Install dependencies if needed
echo "Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies from requirements.txt..."
    python3 -m pip install --break-system-packages -q -r requirements.txt
    echo "✓ Dependencies installed"
fi

# Load environment variables
set -a
source .env
set +a

echo "✓ Loaded .env configuration"
echo ""
echo "Starting API Gateway on ${API_HOST}:${API_PORT}..."
echo "Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python3 -m backend.api_gateway.api_gateway
