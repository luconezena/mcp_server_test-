# Script PowerShell per avviare il server HTTP/SSE
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Avvio MCP Server HTTP/SSE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "ERRORE: Ambiente virtuale non trovato!" -ForegroundColor Red
    Write-Host "Esegui prima: py -m venv venv" -ForegroundColor Yellow
    Read-Host "Premi Enter per uscire"
    exit 1
}

Write-Host "Attivazione ambiente virtuale..." -ForegroundColor Green
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Server in avvio su http://localhost:8000" -ForegroundColor Green
Write-Host "Premi Ctrl+C per fermare il server" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& ".\venv\Scripts\python.exe" "server_http.py"
