import httpx
from app.core.config import settings
from app.core.exceptions import ExternalAPIException

async def get_realtime_quote(symbol: str) -> dict:
    if not settings.TWELVEDATA_API_KEY:
        raise ExternalAPIException("TWELVEDATA_API_KEY is not configured", 401, "TwelveData")
        
    url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={settings.TWELVEDATA_API_KEY}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            data = response.json()
        except httpx.RequestError as e:
            raise ExternalAPIException(f"Network error while calling TwelveData: {str(e)}", 502, "TwelveData")
            
    # Check for TwelveData's specific error formats (Quota exhausted etc.)
    if "code" in data and "status" in data and data["status"] == "error":
        if data["code"] == 429:
            raise ExternalAPIException("API rate limit exceeded / Quota exhausted", 429, "TwelveData")
        else:
            raise ExternalAPIException(data.get("message", "Unknown API Error"), data["code"], "TwelveData")
            
    # If quote successful
    if "symbol" in data and "previous_close" in data:
        return data
        
    raise ExternalAPIException(f"Unexpected response format: {data}", 500, "TwelveData")
