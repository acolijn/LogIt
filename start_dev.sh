# Automatically activate virtual environment if it exists
if [ -d "../venv" ]; then
     source ../venv/bin/activate
     echo "Activated virtual environment."
else
     echo "No virtual environment found at ../venv. Skipping activation."
fi

#!/bin/bash
# Development startup script for LogIt
# Starts MongoDB and Flask, stops both on Ctrl+C

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down..."
    
    # Stop Flask (if running)
    if [ -n "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null || true
    fi
    
    # Stop MongoDB
    if [ -n "$MONGO_PID" ]; then
        kill $MONGO_PID 2>/dev/null || true
        echo "MongoDB stopped"
    fi
    
    exit 0
}

trap cleanup SIGINT SIGTERM


# Check if MongoDB is running
if ! lsof -Pi :27017 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "ERROR: MongoDB is not running on port 27017. Please start the MongoDB service (logit-mongodb) first."
    exit 1
fi
echo "MongoDB is running."

# Start Flask
echo "Starting Flask..."
python3 run.py &
FLASK_PID=$!

echo ""
echo "========================================"
echo "  LogIt Development Server Running"
echo "========================================"
echo "  Flask:   http://localhost:5001"
echo "  MongoDB: localhost:27017"
echo ""
echo "  Press Ctrl+C to stop"
echo "========================================"
echo ""

# Wait for processes
wait
