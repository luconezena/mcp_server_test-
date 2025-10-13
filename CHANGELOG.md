# Changelog - Correzioni Server HTTP/SSE

## v1.1 - Correzione architettura SSE (9 ottobre 2025)

### 🔧 Problema risolto

**Problema originale:**
Il server usava `request._send` di FastAPI per gestire la connessione SSE, ma questo approccio era fragile:
- `request._send` è un'API privata (underscore)
- Non garantita tra versioni
- Causava instabilità nella connessione

### ✅ Soluzione implementata

**Nuovo approccio - ASGI app raw montata:**

```python
async def sse_asgi_app(scope, receive, send):
    """ASGI app con accesso diretto a scope/receive/send"""
    transport = SseServerTransport("/messages")
    async with transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
        init_options = mcp_server.create_initialization_options()
        await mcp_server.run(read_stream, write_stream, init_options)

app.mount("/sse", sse_asgi_app)
```

**Vantaggi:**
- ✅ Usa API ASGI standard (scope, receive, send)
- ✅ Stabile e robusto
- ✅ Compatibile con SseServerTransport di MCP
- ✅ Non dipende da API private

### 📦 Dipendenze aggiornate

**Prima:**
```txt
mcp>=1.0.0
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sse-starlette>=1.8.0
```

**Dopo:**
```txt
mcp>=1.0.0
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
```

**Note:**
- `sse-starlette` rimosso (non necessario, SSE fornito da MCP)
- FastAPI aggiornato a v0.111.0+
- Uvicorn aggiornato a v0.30.0+

### 📝 File aggiunti

1. **`start_server.bat`** - Script batch per Windows
2. **`start_server.ps1`** - Script PowerShell per avvio rapido
3. **`TECHNICAL_NOTES.md`** - Note tecniche sull'architettura
4. **`CHANGELOG.md`** - Questo file

### 🎯 Test di verifica

Per verificare che tutto funzioni:

1. Avvia il server: `.\start_server.ps1`
2. Testa health: `curl http://localhost:8000/health`
3. Verifica info: `curl http://localhost:8000/`
4. Test ChatGPT: Connetti a `http://localhost:8000/sse`

### 🔗 Riferimenti

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [ASGI Specification](https://asgi.readthedocs.io/)
- [FastAPI Sub Applications](https://fastapi.tiangolo.com/advanced/sub-applications/)

## v1.0 - Release iniziale

- Server MCP STDIO base
- Server MCP HTTP/SSE (versione iniziale)
- Tool `ping` implementato
- Documentazione completa
