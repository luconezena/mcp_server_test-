import logging
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from gelato.models import BalanceInput, WhatsappInput, Item
from gelato.ranges import DEFAULT_SOFT, DEFAULT_CLASSICO
from gelato.calc_core import calcola_parametri, dentro_range, ribilancia, nota_base50
from gelato.whatsapp import format_whatsapp

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
server = Server("gelato_mcp_stdio")

@server.list_tools()
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

@server.call_tool()
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
        return [TextContent(type="text", text=str(out))]

    if name == "export_whatsapp":
        data = WhatsappInput(**arguments)
        text = format_whatsapp(data.ricetta, data.parametri, data.target, data.stile, data.lingua)
        return [TextContent(type="text", text=text)]

    raise ValueError(f"Tool sconosciuto: {name}")

if __name__ == "__main__":
    async def main():
        async with stdio_server() as (r, w):
            await server.run(r, w, server.create_initialization_options())
    asyncio.run(main())
