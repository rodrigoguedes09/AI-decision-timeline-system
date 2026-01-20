# Start Script for AI Decision Timeline
# Starts both backend and frontend servers

Write-Host "AI Decision Timeline - Starting..." -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if setup was run
if (-not (Test-Path "backend\venv")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup first:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1" -ForegroundColor White
    exit 1
}

if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "[ERROR] Node modules not found!" -ForegroundColor Red
    Write-Host "Please run setup first:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1" -ForegroundColor White
    exit 1
}

Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Write-Host "  Backend will run on: http://localhost:8001" -ForegroundColor Cyan
Write-Host "  API Docs available at: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8001"

Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "  Frontend will run on: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"

Write-Host ""
Write-Host "[OK] Servers are starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "Wait a few seconds, then open your browser:" -ForegroundColor Cyan
Write-Host "  http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "To stop the servers:" -ForegroundColor Yellow
Write-Host "  - Close the PowerShell windows" -ForegroundColor White
Write-Host "  - Or press Ctrl+C in each window" -ForegroundColor White
Write-Host ""
