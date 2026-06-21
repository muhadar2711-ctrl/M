from fastapi import APIRouter
from app.services.mt5_bridge import execute_trade, get_balance, get_positions
from app.schemas.mt5 import MT5TradeRequest, MT5ExecutionResult, MT5BalanceResult, MT5PositionsResult

router = APIRouter()

@router.post("/execute", response_model=MT5ExecutionResult)
async def mt5_execute_trade(trade: MT5TradeRequest):
    """
    Execute order (Buy/Sell/Close) by forwarding securely to local MT5 EA.
    """
    result = await execute_trade(trade)
    return {"status": "success", "execution_result": result}

@router.get("/balance", response_model=MT5BalanceResult)
async def mt5_account_balance():
    """
    Fetch account balance from remote MT5 EA.
    """
    result = await get_balance()
    return {"status": "success", "balance": result}

@router.get("/positions", response_model=MT5PositionsResult)
async def mt5_open_positions():
    """
    Fetch all active open positions from remote MT5 EA.
    """
    result = await get_positions()
    return {"status": "success", "positions": result}
