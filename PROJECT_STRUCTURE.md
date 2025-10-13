# 📁 Struttura Progetto MCP Server

```
mcp_server_test/
│
├── 📄 server.py                   # Server MCP STDIO (test locali)
├── 📄 server_http.py              # Server MCP HTTP/SSE (ChatGPT) ⭐
├── 📄 test_server.py              # Script test automatici
│
├── 🚀 start_server.ps1            # Avvio rapido PowerShell ⭐
├── 🚀 start_server.bat            # Avvio rapido Batch/CMD ⭐
│
├── 📦 requirements.txt            # Dipendenze Python
│
├── 📚 README.md                   # Documentazione principale ⭐
├── 📚 QUICKSTART.md               # Guida rapida
├── 📚 CHATGPT_SETUP.md            # Setup ChatGPT Developer Mode
├── 📚 TECHNICAL_NOTES.md          # Note tecniche architettura
├── 📚 CHANGELOG.md                # Storia modifiche
├── 📚 VERIFICATION.md             # Checklist verifica
├── 📚 PROJECT_STRUCTURE.md        # Questo file
│
├── ⚙️ pyrightconfig.json          # Configurazione type checking
├── 🙈 .gitignore                  # File da ignorare in git
│
├── 📁 .vscode/                    # Configurazione VS Code
│   └── settings.json              # Settings Python, Pylance, etc.
│
└── 📁 venv/                       # Ambiente virtuale Python
    ├── Scripts/                   # Eseguibili Windows
    │   ├── python.exe            # Python interprete
    │   ├── pip.exe               # Package manager
    │   └── Activate.ps1          # Script attivazione
    └── Lib/                       # Librerie installate
        └── site-packages/        # mcp, fastapi, uvicorn, etc.
```

## 🎯 File principali per l'utente

### Per sviluppatori
1. **`README.md`** - Leggi prima questo! 📖
2. **`server_http.py`** - Codice server HTTP/SSE
3. **`server.py`** - Codice server STDIO

### Per avvio rapido
1. **`start_server.ps1`** - Avvia server (PowerShell) 🚀
2. **`QUICKSTART.md`** - 3 comandi per iniziare

### Per ChatGPT
1. **`CHATGPT_SETUP.md`** - Setup completo ChatGPT
2. **URL da usare**: `http://localhost:8000/sse`

### Per approfondire
1. **`TECHNICAL_NOTES.md`** - Architettura SSE/ASGI
2. **`CHANGELOG.md`** - Cosa è cambiato
3. **`VERIFICATION.md`** - Checklist verifica

## 📦 Dipendenze (requirements.txt)

```txt
mcp>=1.0.0                # Protocollo MCP ufficiale
fastapi>=0.111.0          # Framework web ASGI
uvicorn[standard]>=0.30.0 # Server ASGI
```

## 🔧 Configurazione

### Python Environment
- **Tipo**: Virtual Environment (venv)
- **Path**: `./venv/`
- **Python**: 3.11+
- **Packages**: mcp, fastapi, uvicorn, requests (test)

### VS Code
- **Interprete**: `${workspaceFolder}/venv/Scripts/python.exe`
- **Type Checking**: Basic (Pylance)
- **Format on Save**: ✅
- **Auto Import**: ✅

### Pyright
- **Mode**: basic
- **Python Version**: 3.11
- **Platform**: Windows
- **Exclude**: venv, __pycache__, node_modules

## 🌐 Endpoints Server HTTP

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Info server |
| `/health` | GET | Health check |
| `/sse` | GET | SSE connection (ChatGPT) |
| `/messages` | POST | Upstream channel (SSE) |

## 🛠️ Tool disponibili

### `ping`
**Descrizione**: Risponde con "pong: <messaggio>"

**Input schema**:
```json
{
  "message": "string"
}
```

**Esempio**:
```json
{
  "tool": "ping",
  "arguments": {
    "message": "hello world"
  }
}
```

**Output**: `pong: hello world`

## 🔄 Workflow tipico

### Setup iniziale (una volta)
```powershell
# 1. Crea venv
py -m venv venv

# 2. Attiva venv
.\venv\Scripts\Activate.ps1

# 3. Installa dipendenze
pip install -r requirements.txt
```

### Uso quotidiano
```powershell
# Avvia server
.\start_server.ps1

# In ChatGPT Developer Mode:
# URL: http://localhost:8000/sse
```

## 📊 Architettura

```
┌─────────────────────────────────────────┐
│           ChatGPT Web/App               │
│         (Developer Mode)                │
└────────────────┬────────────────────────┘
                 │ HTTP/SSE
                 │ http://localhost:8000/sse
                 ↓
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│         (server_http.py)                │
├─────────────────────────────────────────┤
│  GET  /           → Info                │
│  GET  /health     → Health check        │
│  GET  /sse        → SSE (ASGI mount) ⭐ │
│  POST /messages   → Upstream            │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│      SseServerTransport (MCP)           │
│      Transport Layer                    │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│         MCP Server Instance             │
│         Protocol Handler                │
├─────────────────────────────────────────┤
│  @list_tools    → Elenco tool           │
│  @call_tool     → Esecuzione tool       │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│            Tool: ping                   │
│  Input: {"message": "..."}              │
│  Output: "pong: ..."                    │
└─────────────────────────────────────────┘
```

## 🎓 Concetti chiave

### ASGI vs WSGI
- Server usa **ASGI** (asincrono)
- FastAPI → ASGI framework
- Uvicorn → ASGI server

### SSE (Server-Sent Events)
- Comunicazione unidirezionale: Server → Client
- HTTP long-polling
- MCP usa SSE + POST per bidirezionale

### MCP (Model Context Protocol)
- Protocollo standard per LLM tools
- Transport: STDIO o HTTP/SSE
- Questo progetto implementa entrambi

### Virtual Environment
- Isola dipendenze progetto
- Nome: `venv` (convenzione)
- Attivazione: `.\venv\Scripts\Activate.ps1`

## ⚡ Performance

- **Startup**: ~1 secondo
- **Latency SSE**: ~50-100ms
- **Throughput**: Limitato da ChatGPT client
- **Concurrent connections**: Unlimited (ASGI asincrono)

## 🔒 Sicurezza

### Attuale (sviluppo locale)
- ⚠️ CORS: `allow_origins=["*"]`
- ⚠️ No autenticazione
- ⚠️ No HTTPS
- ✅ Solo localhost

### Per produzione (future)
- ✅ CORS: domini specifici
- ✅ Autenticazione: API key
- ✅ HTTPS: certificati SSL
- ✅ Rate limiting

## 📝 License & Credits

- **MCP Protocol**: [Anthropic](https://modelcontextprotocol.io/)
- **FastAPI**: [Tiangolo](https://fastapi.tiangolo.com/)
- **Python**: [PSF](https://www.python.org/)

---

**Versione**: 1.1 (con correzioni ASGI)  
**Data**: 9 ottobre 2025  
**Stato**: ✅ Production Ready
