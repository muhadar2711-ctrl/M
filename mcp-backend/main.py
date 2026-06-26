from mcp.server.fastmcp import FastMCP
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from fastapi import FastAPI

# 1. Server MCP buat ChatGPT
mcp = FastMCP("Sigai")

@mcp.tool()
def sinyal_xauusd():
    """Ambil sinyal XAUUSD terbaru dari SMC"""
    return "Sinyal SMC: Tunggu konfirmasi BUY di atas 2650"

# 2. API Lama lu tetep jalan
api_lama = FastAPI(title="Server MCP Perdagangan SMC")
#... router lu yang lama taruh di sini...

# 3. Gabungin jadi 1 app
app = Starlette(routes=[
    Mount('/mcp', app=mcp.sse_app()), # <- INI WAJIB BUAT CHATGPT
    Mount('/', app=api_lama), # <- API lama lu
])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
