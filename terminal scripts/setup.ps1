# Setup Script for AI Decision Timeline
# Automates the initial setup process

Write-Host "AI Decision Timeline - Setup Script" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.9+ from python.org" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 16+ from nodejs.org" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting up Backend..." -ForegroundColor Cyan
Write-Host "-------------------------" -ForegroundColor Cyan

# Backend setup
Set-Location backend

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "Loading demo data..." -ForegroundColor Yellow
python scripts/load_demo_data.py

Set-Location ..

Write-Host ""
Write-Host "Setting up Frontend..." -ForegroundColor Cyan
Write-Host "-------------------------" -ForegroundColor Cyan

# Frontend setup
Set-Location frontend

Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
npm install

Set-Location ..

Write-Host ""
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the system, run:" -ForegroundColor Cyan
Write-Host "  .\start.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or manually:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 (Backend):" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  .\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 (Frontend):" -ForegroundColor Yellow
Write-Host "  cd frontend" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Then visit: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  - README.md - Project overview" -ForegroundColor White
Write-Host "  - QUICKSTART.md - Detailed guide" -ForegroundColor White
Write-Host "  - API Docs: http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
