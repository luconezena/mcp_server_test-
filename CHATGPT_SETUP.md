# Guida rapida: Integrare con ChatGPT Developer Mode

## 🚀 Setup rapido (3 passi)

### 1. Attiva l'ambiente virtuale e installa le dipendenze
```powershell
# Attiva venv (se non già attivo)
.\venv\Scripts\Activate.ps1

# Installa/aggiorna le dipendenze
pip install -r requirements.txt
```

### 2. Avvia il server HTTP
```powershell
python server_http.py
```

Vedrai un output tipo:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Configura ChatGPT Developer Mode

1. Vai su **ChatGPT** (web o app)
2. Attiva **Developer Mode** (nelle impostazioni o nel menu)
3. Aggiungi un nuovo **MCP Server**:
   - **Nome**: `MCP Ping Server`
   - **URL**: `http://localhost:8000/sse`
   - **Tipo**: `SSE` (Server-Sent Events)

4. Salva e attendi la connessione ✅

## 🎯 Come usare

Una volta connesso, ChatGPT avrà accesso al tool `ping`. Puoi chiedere:

```
"Usa il tool ping con il messaggio 'hello world'"
```

ChatGPT risponderà con:
```
pong: hello world
```

## 🔍 Verifica che funzioni

### Test 1: Health check
Apri il browser su: `http://localhost:8000/health`

Dovresti vedere:
```json
{"status": "healthy"}
```

### Test 2: Info del server
Apri: `http://localhost:8000/`

Vedrai le info del server e gli endpoint disponibili.

### Test 3: Log del server
Nel terminale dove hai avviato `server_http.py` vedrai i log di ogni richiesta:
- Connessioni SSE
- Chiamate ai tool
- Risposte generate

## ⚠️ Troubleshooting

### Problema: "Connection refused"
- Verifica che il server sia in esecuzione
- Controlla che la porta 8000 non sia occupata

### Problema: "CORS error"
- Il server è già configurato per accettare richieste da qualsiasi origine
- Se usi un proxy, verifica le sue impostazioni

### Problema: ChatGPT non vede il tool
- Riavvia la connessione in Developer Mode
- Controlla i log del server per errori
- Verifica che l'URL sia esattamente `http://localhost:8000/sse`

## 🌐 Accesso remoto (opzionale)

Se vuoi usare il server da un altro dispositivo o rendere pubblico il server:

### Opzione 1: Tunnel con ngrok
```powershell
ngrok http 8000
```

Poi usa l'URL ngrok in ChatGPT: `https://xxxx.ngrok.io/sse`

### Opzione 2: Tunnel con cloudflared
```powershell
cloudflared tunnel --url http://localhost:8000
```

## 📝 Note

- Il server HTTP/SSE e il server STDIO hanno **esattamente gli stessi tool**
- Cambia solo il **transport layer** (HTTP vs STDIO)
- Per sviluppo locale usa STDIO + MCP Inspector
- Per ChatGPT usa HTTP/SSE
