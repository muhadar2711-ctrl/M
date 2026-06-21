import httpx
from app.core.config import settings
from app.core.exceptions import ExternalAPIException

async def analyze_twitter_sentiment(symbol: str) -> dict:
    if not settings.TWITTER_BEARER_TOKEN:
        raise ExternalAPIException("TWITTER_BEARER_TOKEN is not configured", 401, "Twitter")
        
    url = f"https://api.twitter.com/2/tweets/search/recent?query={symbol} -is:retweet&max_results=10"
    headers = {
        "Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}",
        "User-Agent": "MCPTradingBot/1.0"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code == 401:
                raise ExternalAPIException("Invalid Twitter Bearer Token", 401, "Twitter")
            if response.status_code == 429:
                raise ExternalAPIException("Rate limit exceeded for Twitter API", 429, "Twitter")
                
            response.raise_for_status()
            data = response.json()
        except httpx.RequestError as e:
            raise ExternalAPIException(f"Failed to connect to Twitter: {str(e)}", 502, "Twitter")
            
    tweets = data.get("data", [])
    if not tweets:
        return {
            "symbol": symbol,
            "sentiment": "NEUTRAL",
            "confidence_score": 50,
            "source": "Twitter API (No recent data)"
        }
        
    # Algorithmic keyword extraction and scoring
    bullish_keywords = ["buy", "long", "bull", "moon", "up", "breakout", "rally", "higher", "support", "surge"]
    bearish_keywords = ["sell", "short", "bear", "crash", "down", "drop", "dump", "lower", "resistance", "plunge"]
    
    bull_score = 0
    bear_score = 0
    
    for t in tweets:
        text = t.get("text", "").lower()
        if any(b in text for b in bullish_keywords):
            bull_score += 1
        if any(b in text for b in bearish_keywords):
            bear_score += 1
            
    total_signals = bull_score + bear_score
    if total_signals == 0:
        sentiment = "NEUTRAL"
        confidence = 50
    else:
        if bull_score > bear_score:
            sentiment = "BULLISH"
            confidence = int((bull_score / total_signals) * 100)
        elif bear_score > bull_score:
            sentiment = "BEARISH"
            confidence = int((bear_score / total_signals) * 100)
        else:
            sentiment = "NEUTRAL"
            confidence = 50

    confidence = max(50, confidence)
    
    return {
        "symbol": symbol,
        "sentiment": sentiment,
        "confidence_score": confidence,
        "source": "Twitter API"
    }
