import logging
import json
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import argparse

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.sse import SseServerTransport

from .gelato.models import BalanceInput, WhatsappInput, Item
from .gelato.ranges import DEFAULT_SOFT, DEFAULT_CLASSICO
from .gelato.presets import PRESETS
from .gelato.calc_core import calcola_parametri, dentro_range, dentro_range_map, ribilancia, nota_base50, alerts_speciali
from .gelato.whatsapp import format_whatsapp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("gelato_mcp_http")
mcp_server = Server("gelato_mcp_http")

@mcp_server.list_tools()
async def list_tools():
    return [
        Tool(
            name="suggest_targets",
            description="Ritorna i range target consigliati per lo stile indicato",
            inputSchema={"type":"object","properties":{"stile":{"type":"string","enum":["soft","classico"]}},"required":["stile"]}
        ),
        Tool(
            name="balance_recipe",
            description="Calcola parametri, verifica i range e propone una ricetta ribilanciata",
            inputSchema={"type":"object","properties":{"stile":{"type":"string"},"target":{"type":"object"},"ingredienti":{"type":"array"}},"required":["stile","target","ingredienti"]}
        ),
        Tool(
            name="export_whatsapp",
            description="Formatta la ricetta+parametri per WhatsApp",
            inputSchema={"type":"object","properties":{"ricetta":{"type":"array"},"parametri":{"type":"object"},"target":{"type":"object"},"stile":{"type":"string"},"lingua":{"type":"string"}},"required":["ricetta","parametri","target","stile"]}
        ),
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "suggest_targets":
        stile = arguments["stile"]
        t = DEFAULT_SOFT if stile == "soft" else DEFAULT_CLASSICO
        return [TextContent(type="text", text=t.model_dump_json())]

    if name == "balance_recipe":
        data = BalanceInput(**arguments)
        p = calcola_parametri([Item(**i.model_dump()) for i in data.ingredienti])
        entro = dentro_range(p, data.target)
        ricetta_new, sugg = ribilancia([Item(**i.model_dump()) for i in data.ingredienti], p, data.target)
        note = nota_base50(ricetta_new)
        out = {
            "totale_kg": round(sum(i.grammi for i in ricetta_new)/1000.0, 3),
            "parametri": p.model_dump(),
            "entro_range": entro,
            "suggerimenti": sugg,
            "ricetta_ribilanciata": [i.model_dump() for i in ricetta_new],
            "note": note
        }
        # Serializzazione sicura in stringa JSON (evita memoryview.decode)
        return [TextContent(type="text", text=json.dumps(out, ensure_ascii=False))]

    if name == "export_whatsapp":
        data = WhatsappInput(**arguments)
        text = format_whatsapp(data.ricetta, data.parametri, data.target, data.stile, data.lingua)
        return [TextContent(type="text", text=text)]

    raise ValueError(f"Tool sconosciuto: {name}")

APP_ENV = os.getenv("APP_ENV", "development").lower()
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
DEBUG_ENABLED = os.getenv("ENABLE_DEBUG")
if DEBUG_ENABLED is None:
    DEBUG_ENABLED = "0" if APP_ENV == "production" else "1"
DEBUG_ENABLED = DEBUG_ENABLED == "1"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Avvio MCP HTTP/SSE... (env=%s, debug=%s)", APP_ENV, DEBUG_ENABLED)
    yield
    logger.info("Shutdown MCP HTTP/SSE...")

app = FastAPI(
    title="Gelato MCP Server",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if APP_ENV == "production" else "/docs",
    redoc_url=None,
    openapi_url=None if APP_ENV == "production" else "/openapi.json",
)

origins = None
if ALLOWED_ORIGINS:
    origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]
else:
    origins = ["*"]  # default aperto; restringere via env in produzione

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"name": "Gelato MCP Server", "version": "1.0.0", "status": "running", "endpoints": {"sse": "/sse", "health": "/health"}}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# --- SSE ASGI app (senza usare API private di FastAPI)
async def sse_asgi_app(scope, receive, send):
    if scope["type"] != "http":
        return
    logger.info(f"Nuova connessione SSE da {scope.get('client')}")
    transport = SseServerTransport("/messages")
    try:
        async with transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
            init_options = mcp_server.create_initialization_options()
            await mcp_server.run(read_stream, write_stream, init_options)
    except Exception as e:
        logger.error(f"Errore SSE: {e}", exc_info=True)
        try:
            await send({"type":"http.response.body","body":f"event: error\ndata: {str(e)}\n\n".encode(),"more_body":False})
        except Exception:
            pass

app.mount("/sse", sse_asgi_app)

# Endpoint upstream per i messaggi SSE: ChatGPT invierà a /sse/messages
@app.post("/sse/messages")
async def handle_messages(request: Request):
    data = await request.json()
    logger.info(f"Messaggio ricevuto: {data}")
    return JSONResponse({"status": "received"})

# (Opzionale) Compat: mantieni anche /messages se altri client lo usano
@app.post("/messages")
async def handle_messages_root(request: Request):
    data = await request.json()
    logger.info(f"Messaggio ricevuto (root): {data}")
    return JSONResponse({"status": "received"})

# --------------------
# UI Web semplice per test locale
WEB_DIR = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

@app.get("/ui")
async def ui_root():
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>UI non trovata</h1>", status_code=404)

# Favicon per evitare 404 cosmetico
@app.get("/favicon.ico")
async def favicon():
    fav = WEB_DIR / "favicon.svg"
    if fav.exists():
        return FileResponse(str(fav), media_type="image/svg+xml")
    return HTMLResponse(status_code=204)

# --------------------
if DEBUG_ENABLED:
    # Endpoint REST di debug (non MCP) per test locale
    # Nota: in produzione vengono disabilitati
    @app.post("/debug/suggest_targets")
    async def debug_suggest_targets(payload: dict):
        stile = payload.get("stile", "soft")
        t = DEFAULT_SOFT if stile == "soft" else DEFAULT_CLASSICO
        return JSONResponse(t.model_dump())

    @app.post("/debug/balance_recipe")
    async def debug_balance_recipe(payload: dict):
        data = BalanceInput(**payload)
        ric = [Item(**i.model_dump()) for i in data.ingredienti]
        p = calcola_parametri(ric)
        entro_map = dentro_range_map(p, data.target)
        ricetta_new, sugg = ribilancia(ric, p, data.target)
        note = nota_base50(ricetta_new)
        special = alerts_speciali(ricetta_new)
        out = {
            "totale_kg": round(sum(i.grammi for i in ricetta_new)/1000.0, 3),
            "parametri": p.model_dump(),
            "entro_range": entro_map,
            "suggerimenti": sugg,
            "alerts": special,
            "neutro_5_g": round((sum(i.grammi for i in ricetta_new)/1000.0) * 5.0, 3),
            "ricetta_ribilanciata": [i.model_dump() for i in ricetta_new],
            "note": note
        }
        return JSONResponse(out)

    @app.post("/debug/export_whatsapp")
    async def debug_export_whatsapp(payload: dict):
        data = WhatsappInput(**payload)
        text = format_whatsapp(data.ricetta, data.parametri, data.target, data.stile, data.lingua)
        return JSONResponse({"text": text})

    # Presets helper per UI
    @app.get("/debug/presets")
    async def debug_list_presets():
        return JSONResponse(sorted(list(PRESETS.keys())))

    @app.get("/debug/preset/{name}")
    async def debug_get_preset(name: str):
        if name in PRESETS:
            return JSONResponse([i.model_dump() for i in PRESETS[name]])
        return JSONResponse({"error": "preset non trovato"}, status_code=404)

if __name__ == "__main__":
    # Avvia direttamente l'istanza app per evitare ambiguità di import (server_http omonimo altrove)
    default_port = int(os.getenv("PORT", "8000"))
    default_host = os.getenv("HOST", "0.0.0.0")
    parser = argparse.ArgumentParser(description="Avvio Il Gelato Artigianale Italiano HTTP/SSE server")
    parser.add_argument("--port", "-p", type=int, default=default_port, help="Porta di ascolto (default: 8000 o $PORT)")
    parser.add_argument("--host", "-H", default=default_host, help="Host di ascolto (default: 0.0.0.0 o $HOST)")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "info"), help="Livello log Uvicorn")
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)
