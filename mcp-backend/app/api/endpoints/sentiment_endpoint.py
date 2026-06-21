from fastapi import APIRouter, Query
from app.services.sentiment import analyze_twitter_sentiment
from app.schemas.sentiment import SentimentAnalysisResult

router = APIRouter()

@router.get("/twitter", response_model=SentimentAnalysisResult)
async def fetch_twitter_sentiment(symbol: str = Query("XAUUSD", description="Symbol to search sentiment for")):
    """
    Integrates with Twitter API to fetch sentiment.
    Returns JSON with sentiment and confidence score.
    """
    return await analyze_twitter_sentiment(symbol)
