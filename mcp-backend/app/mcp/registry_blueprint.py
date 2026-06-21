DOMAINS = [
    "market_data", "execution", "news", "chat", "sentiment"
]

MCPS_BLUEPRINT = [
    {"id": "mcp-md-twelvedata", "name": "TwelveData Feed", "domain": "market_data", "env": ["TWELVEDATA_API_KEY"]},
    
    {"id": "mcp-exec-ea", "name": "Local MT5 Webhook Bridge", "domain": "execution", "env": ["MT5_WEBHOOK_URL", "MT5_WEBHOOK_SECRET"]},
    
    {"id": "mcp-news-forexfactory", "name": "ForexFactory Priority Calendar", "domain": "news", "env": []},
    {"id": "mcp-news-investing", "name": "Investing.com Scraper", "domain": "news", "env": []},
    {"id": "mcp-sentiment-twitter", "name": "Twitter/X AI Sentiment", "domain": "sentiment", "env": ["TWITTER_BEARER_TOKEN"]},
    
    {"id": "mcp-chat-engine", "name": "AI Chat Router", "domain": "chat", "env": ["GEMINI_API_KEY"]},
    {"id": "mcp-chat-context", "name": "AI Context Builder", "domain": "chat", "env": []},
    {"id": "mcp-chat-memory", "name": "AI Memory Manager", "domain": "chat", "env": []},
    {"id": "mcp-chat-rag", "name": "AI RAG Retriever", "domain": "chat", "env": []},
    {"id": "mcp-chat-validator", "name": "AI Response Validator", "domain": "chat", "env": []},
]
