# MCP Server Test

Server MCP minimale che implementa un tool `ping` che risponde con "pong: <messaggio>".

Disponibile in due versioni:
- **`server.py`**: Versione STDIO per test locali e integrazione con MCP Inspector
- **`server_http.py`**: Versione HTTP/SSE per integrazione con ChatGPT Developer Mode

## Requisiti

- Python 3.11 o superiore
- pip

## Installazione e Avvio

### Quick Start - 3 comandi:

1. **Attiva l'ambiente virtuale** (se non già attivo):
```powershell
.\venv\Scripts\Activate.ps1
```

2. **Installa le dipendenze**:
```powershell
pip install -r requirements.txt
```

3. **Avvia il server**:
```powershell
python server.py
```

### Prima configurazione completa:

Se è la prima volta che configuri il progetto:

1. **Crea un ambiente virtuale** (opzionale ma consigliato):
```powershell
python -m venv venv
```

2. **Attiva l'ambiente virtuale**:
```powershell
.\venv\Scripts\Activate.ps1
```

3. **Installa le dipendenze**:
```powershell
pip install -r requirements.txt
```

4. **Avvia il server**:
```powershell
python server.py
```

Il server rimarrà in ascolto e comunicherà tramite standard input/output. Per fermarlo, premi `Ctrl+C` (verrà eseguito un graceful shutdown).

### Avvio versione HTTP/SSE (per ChatGPT):

Per avviare il server HTTP/SSE su `http://localhost:8000`:

**Opzione 1 - Script automatico (consigliato):**
```powershell
.\start_server.ps1
```

**Opzione 2 - Manuale:**
```powershell
.\venv\Scripts\Activate.ps1
python server_http.py
```

Il server sarà accessibile su:
- **Endpoint SSE**: `http://localhost:8000/sse`
- **Health check**: `http://localhost:8000/health`
- **Info**: `http://localhost:8000/`

## Test del server

### Test versione STDIO:

Per testare la versione STDIO, puoi utilizzare l'MCP Inspector:

```powershell
npx @modelcontextprotocol/inspector python server.py
```

### Test versione HTTP/SSE:

1. **Test con browser**: Apri `http://localhost:8000` per vedere le info del server

2. **Test con curl** (health check):
```powershell
curl http://localhost:8000/health
```

3. **Integrazione con ChatGPT Developer Mode**:
   - Avvia il server: `python server_http.py`
   - Vai su ChatGPT e attiva "Developer Mode"
   - Configura l'endpoint: `http://localhost:8000/sse`
   - ChatGPT potrà ora usare il tool `ping`!

## Funzionalità

### Tool disponibili:

- **ping**: Accetta una stringa come parametro `message` e risponde con `"pong: <stringa ricevuta>"`

### Esempio di utilizzo:

Quando il tool `ping` viene chiamato con:
```json
{
  "message": "ciao mondo"
}
```

Risponde con:
```
pong: ciao mondo
```

## Logging

Il server include logging basilare che mostra:
- Quando viene richiesta la lista dei tool
- Quando viene chiamato un tool
- I parametri ricevuti e la risposta generata
