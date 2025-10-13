@echo off
echo ========================================
echo Avvio MCP Server HTTP/SSE
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo ERRORE: Ambiente virtuale non trovato!
    echo Esegui prima: py -m venv venv
    pause
    exit /b 1
)

echo Attivazione ambiente virtuale...
call venv\Scripts\activate.bat

echo.
echo Server in avvio su http://localhost:8000
echo Premi Ctrl+C per fermare il server
echo.
echo ========================================
echo.

python server_http.py

pause
