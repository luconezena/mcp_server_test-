# Note tecniche - Server HTTP/SSE

## Architettura corretta SSE con FastAPI

### ⚠️ Problema con StreamingResponse

Inizialmente il server usava `StreamingResponse` con `request._send`, ma questo approccio ha due problemi:

1. **`request._send` è privato** - Non è parte dell'API pubblica di Starlette/FastAPI
2. **Fragile** - Può rompersi tra versioni diverse

### ✅ Soluzione: ASGI app raw montata

Il server ora usa un'app ASGI "grezza" montata su `/sse`:

```python
async def sse_asgi_app(scope, receive, send):
    """ASGI app con accesso diretto a scope/receive/send"""
    if scope["type"] != "http":
        return
    
    transport = SseServerTransport("/messages")
    async with transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
        init_options = mcp_server.create_initialization_options()
        await mcp_server.run(read_stream, write_stream, init_options)

app.mount("/sse", sse_asgi_app)
```

### Vantaggi

1. **Accesso diretto** a `scope`, `receive`, `send` (API ASGI standard)
2. **Stabile** - Non dipende da API private
3. **Compatibile** con `SseServerTransport` della libreria `mcp`

## Transport SSE bidirezionale

Il transport SSE di MCP usa due canali:

1. **`/sse` (GET)** - Server → Client (eventi SSE)
2. **`/messages` (POST)** - Client → Server (messaggi upstream)

Entrambi gli endpoint sono necessari per la comunicazione completa.

## Testing

### Test manuale con curl

```powershell
# Health check
curl http://localhost:8000/health

# Info server
curl http://localhost:8000/

# Test connessione SSE (rimarrà aperto)
curl http://localhost:8000/sse
```

### Test con ChatGPT Developer Mode

1. Avvia il server: `python server_http.py`
2. In ChatGPT, Developer Mode → Add MCP Server
3. URL: `http://localhost:8000/sse`
4. Testa con: "Usa il tool ping con 'test'"

## Dipendenze critiche

```txt
mcp>=1.0.0              # Libreria MCP ufficiale
fastapi>=0.111.0        # FastAPI aggiornato
uvicorn[standard]>=0.30.0  # Server ASGI con WebSockets
```

**Nota**: Non serve più `sse-starlette` - il transport SSE è fornito da `mcp`.

## Riferimenti

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastAPI ASGI Mounting](https://fastapi.tiangolo.com/advanced/sub-applications/)
- [ASGI Specification](https://asgi.readthedocs.io/)
