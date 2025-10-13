# 🚀 Quick Start - MCP Server

## Avvio rapido in 3 comandi

### Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\start_server.ps1
```

### Windows (CMD):
```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
start_server.bat
```

## Verifica funzionamento

1. **Health check**: Apri http://localhost:8000/health
2. **Info server**: Apri http://localhost:8000/

## Integrazione ChatGPT

1. Server avviato ✅
2. ChatGPT → Developer Mode
3. Add MCP Server:
   - **URL**: `http://localhost:8000/sse`
   - **Nome**: `MCP Ping Server`
4. Testa: *"Usa il tool ping con 'hello world'"*
5. Risposta attesa: `pong: hello world` ✅

## File principali

| File | Descrizione |
|------|-------------|
| `server.py` | Server STDIO per test locali |
| `server_http.py` | Server HTTP/SSE per ChatGPT |
| `start_server.ps1` | Avvio rapido (PowerShell) |
| `start_server.bat` | Avvio rapido (Batch) |
| `test_server.py` | Test automatici |

## Documentazione

- 📖 **README.md** - Guida completa
- 🎯 **CHATGPT_SETUP.md** - Setup ChatGPT
- 🔧 **TECHNICAL_NOTES.md** - Note tecniche
- 📝 **CHANGELOG.md** - Storia modifiche

## Troubleshooting

### Porta 8000 occupata?
```powershell
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess | Stop-Process -Force
```

### Dipendenze mancanti?
```powershell
pip install -r requirements.txt
```

### Server non risponde?
Verifica che l'ambiente virtuale sia attivo: `(venv)` nel prompt

## Architettura

```
┌─────────────────┐
│   ChatGPT       │
│ Developer Mode  │
└────────┬────────┘
         │ HTTP/SSE
         ↓
┌─────────────────┐
│  FastAPI App    │
│  localhost:8000 │
├─────────────────┤
│ GET  /          │ Info
│ GET  /health    │ Health check
│ GET  /sse       │ SSE endpoint (ASGI)
│ POST /messages  │ Upstream channel
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   MCP Server    │
│   Tool: ping    │
└─────────────────┘
```

## Tool disponibili

### `ping`
**Input**: `{"message": "testo"}`  
**Output**: `"pong: testo"`

**Esempio**:
```json
{
  "tool": "ping",
  "arguments": {
    "message": "hello world"
  }
}
```

**Risposta**:
```
pong: hello world
```
