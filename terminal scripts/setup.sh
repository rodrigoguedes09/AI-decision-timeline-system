#!/bin/bash
# Setup Script for AI Decision Timeline (macOS/Liecho ""
echo "Setup Complete!"
echo "==============="
echo ""
echo "To start the system:"# Automates the initial setup process

echo "AI Decision Timeline - Setup Script"
echo "======================================="
echo ""

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "[OK] Found: $PYTHON_VERSION"
else
    echo "[ERROR] Python not found. Please install Python 3.9+ from python.org"
    exit 1
fi

# Check Node.js
echo "Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "[OK] Found Node.js: $NODE_VERSION"
else
    echo "[ERROR] Node.js not found. Please install Node.js 16+ from nodejs.org"
    exit 1
fi

echo ""
echo "Setting up Backend..."
echo "-------------------------"

# Backend setup
cd backend

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Loading demo data..."
python scripts/load_demo_data.py

cd ..

echo ""
echo "Setting up Frontend..."
echo "-------------------------"

# Frontend setup
cd frontend

echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "Setup Complete!"
echo "=================="
echo ""
echo "To start the system:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then visit: http://localhost:3000"
echo ""
echo "Documentation:"
echo "  - README.md - Project overview"
echo "  - QUICKSTART.md - Detailed guide"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
