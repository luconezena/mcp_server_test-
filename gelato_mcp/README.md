# Gelato MCP Server

Server MCP per bilanciamento ricette gelato (MVP). Espone 3 tool: suggest_targets, balance_recipe, export_whatsapp.

## Requisiti
- Python 3.11+
- `pip install -r requirements.txt`

## Avvio
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
pip install -r requirements.txt
python server_http.py


Test rapido:

http://localhost:8000/
 → running

http://localhost:8000/health
 → healthy
