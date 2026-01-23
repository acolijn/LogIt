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

# Create data directory if needed
mkdir -p mongodb_data

# Start MongoDB (use local binary if available)
echo "Starting MongoDB..."
if [ -x "./mongodb/bin/mongod" ]; then
    ./mongodb/bin/mongod --config mongod.conf &
elif [ -x "./mongodb_bin/mongod" ]; then
    ./mongodb_bin/mongod --config mongod.conf &
else
    mongod --config mongod.conf &
fi
MONGO_PID=$!

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to start..."
sleep 2

# Check if MongoDB is running
if ! kill -0 $MONGO_PID 2>/dev/null; then
    echo "ERROR: MongoDB failed to start. Check mongodb_data/mongod.log"
    exit 1
fi

echo "MongoDB started (PID: $MONGO_PID)"

# Start Flask
echo "Starting Flask..."
python run.py &
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
