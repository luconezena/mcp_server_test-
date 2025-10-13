param(
    [int]$Port = 8000,
    [string]$ListenHost = "0.0.0.0"
)

# Avvio rapido server "Il Gelato Artigianale Italiano" (Windows PowerShell)
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

if (-not (Test-Path "venv/Scripts/python.exe")) {
    Write-Host "Creo venv..."
    py -m venv venv
}

& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server_http.py --host $ListenHost --port $Port
