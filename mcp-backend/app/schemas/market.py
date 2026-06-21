from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class TwelveDataQuoteResponse(BaseModel):
    symbol: str
    name: str
    exchange: str
    mic_code: str
    currency: str
    datetime: str
    timestamp: int
    open: str
    high: str
    low: str
    close: str
    volume: str
    previous_close: str
    change: str
    percent_change: str
    average_volume: str
    is_market_open: bool
    fifty_two_week: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True, extra="allow")
