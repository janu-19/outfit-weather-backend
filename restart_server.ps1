# Script to stop existing uvicorn servers and restart with Python 3.13

Write-Host "Stopping existing uvicorn servers..." -ForegroundColor Yellow

# Find and stop uvicorn processes
$uvicornProcesses = Get-Process | Where-Object { $_.ProcessName -eq "uvicorn" -or $_.CommandLine -like "*uvicorn*" }
if ($uvicornProcesses) {
    foreach ($proc in $uvicornProcesses) {
        Write-Host "Stopping process $($proc.Id)..." -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
}

# Find and stop python processes that might be running uvicorn
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*Python313*" }
if ($pythonProcesses) {
    Write-Host "Found Python 3.13 processes. Please manually stop your server (Ctrl+C) if it's running in a terminal." -ForegroundColor Yellow
}

Write-Host "`nStarting server with Python 3.13..." -ForegroundColor Green
Write-Host "Command: py -3.13 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server when done." -ForegroundColor Yellow

# Start the server
py -3.13 -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

