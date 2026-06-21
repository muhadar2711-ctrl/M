from fastapi import APIRouter
from app.api.endpoints import market_data, news, sentiment_endpoint, mt5

api_router = APIRouter()

api_router.include_router(mt5.router, prefix="/mt5", tags=["MT5 Execution Bridge"])
api_router.include_router(market_data.router, prefix="/data", tags=["Market Data (TwelveData)"])
api_router.include_router(news.router, prefix="/news", tags=["Economic Calendar"])
api_router.include_router(sentiment_endpoint.router, prefix="/sentiment", tags=["Sentiment Analysis"])
