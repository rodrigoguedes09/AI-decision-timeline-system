# Stop Script for AI Decision Timeline
# Stops all running backend and frontend servers

Write-Host "AI Decision Timeline - Stopping Servers..." -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Stop backend (uvicorn)
Write-Host "Stopping Backend (port 8001)..." -ForegroundColor Yellow
$backend = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
if ($backend) {
    $processId = $backend.OwningProcess
    Stop-Process -Id $processId -Force
    Write-Host "[OK] Backend stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] Backend not running" -ForegroundColor Gray
}

# Stop frontend (Vite)
Write-Host "Stopping Frontend (port 3000)..." -ForegroundColor Yellow
$frontend = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($frontend) {
    $processId = $frontend.OwningProcess
    Stop-Process -Id $processId -Force
    Write-Host "[OK] Frontend stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] Frontend not running" -ForegroundColor Gray
}

Write-Host ""
Write-Host "All servers stopped!" -ForegroundColor Green
Write-Host ""
