import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers
from app.api.router import api_router
from app.chat.api.router import router as chat_router
from app.mcp.registry_blueprint import MCPS_BLUEPRINT

# Setup basic logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SMC Trading MCP Server...")
    # Log MCP readiness summary at startup
    for mcp in MCPS_BLUEPRINT:
        env_ok = all(os.getenv(env_var) for env_var in mcp["env"])
        status = "READY" if env_ok else "MISSING_ENV"
        logger.info("  MCP %s [%s]: %s", mcp["id"], mcp["domain"], status)
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


def _build_mcp_readiness():
    """Build structured MCP readiness list from blueprint + env check."""
    mcps = []
    for mcp in MCPS_BLUEPRINT:
        env_ok = all(os.getenv(env_var) for env_var in mcp["env"])
        mcps.append({
            "id": mcp["id"],
            "name": mcp["name"],
            "domain": mcp["domain"],
            "ready": env_ok,
            "status": "READY" if env_ok else "MISSING_ENV",
        })
    return mcps


@app.get("/", tags=["Health"])
async def root():
    """Liveness probe. No database or external service dependency."""
    return {
        "message": "MCP Server is running",
        "service": "smc-trading-mcp-server",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check probe. Returns minimal status + MCP readiness summary."""
    mcps = _build_mcp_readiness()
    return {
        "status": "ok",
        "service": "smc-trading-mcp-server",
        "version": "1.0.0",
        "mcps": mcps,
    }


@app.get("/health/details", tags=["Health"])
async def health_details():
    """Detailed status of each major service component.

    Backward-compatible: legacy ``services`` dict preserved.
    New ``mcps`` array added for Sigai frontend consumption.
    """
    mcps = _build_mcp_readiness()

    # Legacy services dict – kept for backward compatibility
    legacy_services = {
        "twelvedata": "READY" if os.getenv("TWELVEDATA_API_KEY") else "MISSING_KEY",
        "mt5_bridge": "READY" if os.getenv("MT5_WEBHOOK_URL") else "MISSING_KEY",
        "news_parser": "READY",
        "sentiment_analyzer": (
            "READY" if os.getenv("TWITTER_BEARER_TOKEN") else "MISSING_KEY"
        ),
    }

    return {
        "status": "online",
        "service": "smc-trading-mcp-server",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "mcps": mcps,
        "services": legacy_services,
    }