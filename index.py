# Vercel entrypoint per FastAPI
# Espone l'istanza app già definita nel progetto Gelato MCP
# In caso di errore di import, esponiamo una piccola app diagnostica
try:
	from gelato_mcp.server_http import app as _app  # type: ignore
	app = _app
except Exception as e:
	from fastapi import FastAPI
	import traceback

	_err = f"Import error: {e}\n{traceback.format_exc()}"
	app = FastAPI(title="Gelato MCP (diagnostic)")

	@app.get("/")
	async def diag_root():
		return {"status": "error", "detail": _err}

	@app.get("/health")
	async def diag_health():
		return {"status": "error", "detail": _err}
