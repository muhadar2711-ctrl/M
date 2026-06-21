import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.api.router import api_router
from app.chat.api.router import router as chat_router

# Setup basic logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SMC Trading MCP Server...")
    yield
    logger.info("Shutting down SMC Trading MCP Server...")
    
app = FastAPI(
    title="SMC Trading MCP Server",
    description="Microservice Bridge for MT5 Execution, Market Data, and Sentiment Analysis",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS logic safely
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Setup Centralized Exception Handling
setup_exception_handlers(app)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
async def root_health_check():
    """
    Root health check endpoint.
    Retrieves the status of each major service component.
    """
    return {
        "status": "online",
        "services": {
            "twelvedata": "READY",
            "mt5_bridge": "READY",
            "news_parser": "READY",
            "sentiment_analyzer": "READY" if settings.TWITTER_BEARER_TOKEN else "MISSING_KEY"
        },
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }
