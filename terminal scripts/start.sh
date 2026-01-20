#!/bin/bash
# Start Script for AI Decision Timeline
# Starts both backend and frontend servers

echo "AI Decision Timeline - Starting..."
echo "===================================="
echo ""

# Check if setup was run
if [ ! -d "backend/venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run setup first:"
    echo "  ./setup.sh"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "[ERROR] Node modules not found!"
    echo "Please run setup first:"
    echo "  ./setup.sh"
    exit 1
fi

echo "Starting Backend Server..."
echo "  Backend will run on: http://localhost:8001"
echo "  API Docs available at: http://localhost:8001/docs"
echo ""

# Start backend in background
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
cd ..

echo "Starting Frontend Server..."
echo "  Frontend will run on: http://localhost:3000"
echo ""

# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "[OK] Servers are starting!"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Wait a few seconds, then open your browser:"
echo "  http://localhost:3000"
echo ""
echo "To stop the servers:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or press Ctrl+C to stop this script (servers will keep running)"
echo ""

# Keep script running
wait
