# Quick Start – Gelato MCP

## 1. Setup ambiente
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Avvio server (FastAPI + uvicorn)
```powershell
python server_http.py
# oppure con reload dev
uvicorn server_http:app --host 0.0.0.0 --port 8000 --reload
```

## 3. Test rapido
- http://localhost:8000/
- http://localhost:8000/health

## 4. ChatGPT Developer Mode
Endpoint: `http://localhost:8000/sse`
