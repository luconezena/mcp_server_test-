# Vercel entrypoint per FastAPI
# Espone l'istanza app già definita nel progetto Gelato MCP
from gelato_mcp.server_http import app  # type: ignore
