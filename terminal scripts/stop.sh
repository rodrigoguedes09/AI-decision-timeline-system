#!/bin/bash
# Stop Script for AI Decision Timeline
# Stops all running backend and frontend servers

echo "AI Decision Timeline - Stopping Servers..."
echo "==========================================="
echo ""

# Stop backend (uvicorn on port 8001)
echo "Stopping Backend (port 8001)..."
BACKEND_PID=$(lsof -ti:8001)
if [ ! -z "$BACKEND_PID" ]; then
    kill -9 $BACKEND_PID
    echo "[OK] Backend stopped"
else
    echo "[INFO] Backend not running"
fi

# Stop frontend (Vite on port 3000)
echo "Stopping Frontend (port 3000)..."
FRONTEND_PID=$(lsof -ti:3000)
if [ ! -z "$FRONTEND_PID" ]; then
    kill -9 $FRONTEND_PID
    echo "[OK] Frontend stopped"
else
    echo "[INFO] Frontend not running"
fi

echo ""
echo "All servers stopped!"
echo ""
