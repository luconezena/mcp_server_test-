# ChatGPT Developer Mode – Setup

1) Avvia il server HTTP/SSE:
```powershell
.\start_server.ps1
```

In alternativa (senza script):
```powershell
.\venv\Scripts\Activate.ps1
python server_http.py
```

2) In ChatGPT → Developer Mode → Add MCP Server:
- URL: `http://localhost:8000/sse`
- Nome: `Gelato MCP`

3) Strumenti disponibili:
- `suggest_targets(stile)`
- `balance_recipe(ingredienti, target, stile)`
- `export_whatsapp(ricetta, lingua)`
