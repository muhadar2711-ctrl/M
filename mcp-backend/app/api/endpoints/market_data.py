from fastapi import APIRouter, Query
from app.services.twelvedata import get_realtime_quote
from app.schemas.market import TwelveDataQuoteResponse

router = APIRouter()

@router.get("/twelvedata/quote", response_model=TwelveDataQuoteResponse)
async def fetch_twelvedata_quote(symbol: str = Query("XAU/USD", description="Market symbol, e.g. XAU/USD")):
    """
    Fetch real-time quote from TwelveData API.
    Handles '429 Quota exhausted' gracefully.
    """
    return await get_realtime_quote(symbol)
