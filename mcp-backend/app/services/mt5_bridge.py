import httpx
from typing import Optional
from app.core.config import settings
from app.core.exceptions import ExternalAPIException
from app.schemas.mt5 import MT5TradeRequest

async def send_to_mt5_terminal(endpoint: str, payload: dict) -> dict:
    """
    Acts as a Webhook/ZMQ bridge to a locally running MT5 EA.
    If URL is not configured, returns a clean error indicating setup is needed.
    """
    if not settings.MT5_WEBHOOK_URL:
        raise ExternalAPIException("MT5_WEBHOOK_URL is not configured. Forwarding bridge inactive.", 503, "MT5 Bridge")
        
    headers = {"Content-Type": "application/json"}
    if settings.MT5_WEBHOOK_SECRET:
        headers["X-Webhook-Secret"] = settings.MT5_WEBHOOK_SECRET
        
    full_url = f"{settings.MT5_WEBHOOK_URL.rstrip('/')}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(full_url, json=payload, headers=headers, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise ExternalAPIException(f"Could not connect to MT5 EA at {full_url}", 502, "MT5 Bridge")
        except httpx.HTTPStatusError as e:
            raise ExternalAPIException(f"MT5 EA returned error: {e.response.text}", e.response.status_code, "MT5 Bridge")
        except Exception as e:
            raise ExternalAPIException(f"Unexpected MT5 bridge error: {str(e)}", 500, "MT5 Bridge")

async def execute_trade(trade: MT5TradeRequest) -> dict:
    return await send_to_mt5_terminal("execute", trade.model_dump())

async def get_balance() -> dict:
    return await send_to_mt5_terminal("balance", {})

async def get_positions() -> dict:
    return await send_to_mt5_terminal("positions", {})
