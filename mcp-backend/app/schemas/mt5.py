from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class MT5TradeRequest(BaseModel):
    action: str
    symbol: str
    volume: float
    sl: Optional[float] = None
    tp: Optional[float] = None
    magic_number: int = 123456

    model_config = ConfigDict(from_attributes=True)

class MT5ExecutionResult(BaseModel):
    status: str
    execution_result: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class MT5BalanceResult(BaseModel):
    status: str
    balance: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)

class MT5PositionsResult(BaseModel):
    status: str
    positions: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)
