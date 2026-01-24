#!/bin/bash

echo "Starting AI Chatbot Application..."
echo ""

# Start Backend
echo "[1/2] Starting FastAPI Backend..."
cd "$(dirname "$0")"
python main.py &
BACKEND_PID=$!
sleep 3

# Start Frontend
echo "[2/2] Starting React Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "Application is running!"
echo "========================================"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop both servers..."

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
