"""
Server MCP minimale che espone un tool 'ping'.
Questo server utilizza il protocollo Model Context Protocol (MCP) per comunicare via stdio.
"""

import logging
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configurazione del logging per monitorare le operazioni del server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_server_test")

# Creazione dell'istanza del server MCP
# Il server gestirà le richieste dei client e fornirà i tool disponibili
server = Server("mcp_server_test")

@server.list_tools()
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

@server.call_tool()
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

async def main():
    """
    Funzione principale che avvia il server MCP in modalità stdio.
    Il server comunica attraverso standard input/output, permettendo
    la comunicazione con client MCP.
    """
    logger.info("Avvio del server MCP in modalità stdio...")
    
    # Avvio del server in modalità stdio (standard input/output)
    # Questo permette la comunicazione con i client tramite pipe
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server MCP avviato e in ascolto...")
        
        # Esecuzione del server fino alla terminazione
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

# Punto di ingresso del programma
if __name__ == "__main__":
    logger.info("Inizializzazione del server MCP...")
    
    try:
        # Esecuzione della funzione main usando asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        # Gestione graceful dello shutdown quando l'utente preme Ctrl+C
        logger.info("Server MCP arrestato dall'utente (Ctrl+C)")
        logger.info("Shutdown completato con successo")
    except Exception as e:
        # Logging di eventuali altri errori critici
        logger.error(f"Errore critico durante l'esecuzione del server: {e}", exc_info=True)
