"""
Server MCP HTTP/SSE per integrazione con ChatGPT Developer Mode.
Questo server espone gli stessi tool della versione stdio ma tramite endpoint HTTP.
Compatibile con ChatGPT Developer Mode su http://localhost:8000
"""

import logging
import asyncio
from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.sse import SseServerTransport

# Configurazione del logging per monitorare le operazioni del server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_server_http")

# Creazione dell'istanza del server MCP
# Il server gestirà le richieste dei client e fornirà i tool disponibili
mcp_server = Server("mcp_server_http")

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Elenca i tool disponibili sul server.
    Questa funzione viene chiamata dai client per scoprire quali tool sono disponibili.
    """
    logger.info("Client ha richiesto la lista dei tool disponibili")
    
    return [
        Tool(
            name="ping",
            description=(
                "Risponde con 'pong' seguito dalla stringa ricevuta. "
                "Esempio di payload: {\"message\": \"ciao mondo\"} -> risponde: \"pong: ciao mondo\""
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "La stringa da includere nella risposta"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Gestisce le chiamate ai tool da parte dei client.
    
    Args:
        name: Il nome del tool da eseguire
        arguments: I parametri passati al tool
    
    Returns:
        Una lista di contenuti testuali come risposta
    """
    logger.info(f"Tool chiamato: {name} con argomenti: {arguments}")
    
    # Gestione del tool 'ping'
    if name == "ping":
        # Validazione robusta dell'input
        if not isinstance(arguments, dict) or "message" not in arguments:
            error_msg = "Argomento mancante: 'message'"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Estrazione del messaggio dagli argomenti
        message = arguments.get("message", "")
        
        # Creazione della risposta
        response = f"pong: {message}"
        
        logger.info(f"Risposta generata: {response}")
        
        # Restituzione della risposta come TextContent
        return [TextContent(type="text", text=response)]
    
    # Se il tool richiesto non esiste, solleva un errore
    else:
        error_msg = f"Tool sconosciuto: {name}"
        logger.error(error_msg)
        raise ValueError(error_msg)

# Gestione del ciclo di vita dell'applicazione FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestisce l'avvio e lo shutdown dell'applicazione.
    """
    logger.info("Avvio del server MCP HTTP/SSE...")
    yield
    logger.info("Shutdown del server MCP HTTP/SSE...")

# Creazione dell'applicazione FastAPI
app = FastAPI(
    title="MCP Server HTTP",
    description="Server MCP con transport HTTP/SSE per integrazione ChatGPT",
    version="1.0.0",
    lifespan=lifespan
)

# Configurazione CORS per permettere richieste da ChatGPT e altri client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, specifica i domini consentiti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Endpoint di root per verificare che il server sia attivo.
    """
    return {
        "name": "MCP Server HTTP",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "sse": "/sse",
            "health": "/health"
        }
    }

@app.get("/health")
async def health():
    """
    Endpoint di health check per monitoraggio.
    """
    return {"status": "healthy"}

# --- ENDPOINT SSE CON ASGI APP RAW (VERSIONE CORRETTA) ---

async def sse_asgi_app(scope, receive, send):
    """
    ASGI app raw per l'endpoint SSE.
    Questo approccio permette l'accesso diretto a scope/receive/send
    senza usare il fragile request._send di FastAPI.
    """
    # Accetta solo richieste HTTP (SSE è su HTTP, non WebSocket)
    if scope["type"] != "http":
        return

    logger.info(f"Nuova connessione SSE da {scope.get('client')}")
    
    # Creazione del transport SSE
    transport = SseServerTransport("/messages")

    try:
        # Connessione SSE con accesso diretto a scope/receive/send
        async with transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
            # Inizializzazione delle opzioni del server
            init_options = mcp_server.create_initialization_options()
            
            # Esecuzione del server MCP con i stream SSE
            await mcp_server.run(read_stream, write_stream, init_options)
            
    except Exception as e:
        logger.error(f"Errore nella connessione SSE: {e}", exc_info=True)
        
        # Prova a inviare un evento di errore (best-effort)
        try:
            await send({
                "type": "http.response.body",
                "body": f"event: error\ndata: {str(e)}\n\n".encode("utf-8"),
                "more_body": False
            })
        except Exception:
            pass

# Monta l'app ASGI sotto /sse
# Questo permette la comunicazione SSE con ChatGPT Developer Mode
app.mount("/sse", sse_asgi_app)

@app.post("/messages")
async def handle_messages(request: Request):
    """
    Endpoint POST per ricevere messaggi dal client.
    Utilizzato dal transport SSE per la comunicazione bidirezionale.
    """
    try:
        data = await request.json()
        logger.info(f"Messaggio ricevuto: {data}")
        return JSONResponse({"status": "received"})
    except Exception as e:
        logger.error(f"Errore nella gestione del messaggio: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=400)

# Punto di ingresso del programma
if __name__ == "__main__":
    logger.info("Inizializzazione del server MCP HTTP/SSE...")
    
    try:
        # Configurazione e avvio di uvicorn
        # Il server sarà accessibile su http://localhost:8000
        uvicorn.run(
            app,
            host="0.0.0.0",  # Ascolta su tutte le interfacce
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        # Gestione graceful dello shutdown quando l'utente preme Ctrl+C
        logger.info("Server MCP HTTP arrestato dall'utente (Ctrl+C)")
        logger.info("Shutdown completato con successo")
    except Exception as e:
        # Logging di eventuali altri errori critici
        logger.error(f"Errore critico durante l'esecuzione del server: {e}", exc_info=True)
