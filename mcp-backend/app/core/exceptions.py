import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

class ExternalAPIException(Exception):
    def __init__(self, message: str, status_code: int = 502, provider: str = "External"):
        self.message = message
        self.status_code = status_code
        self.provider = provider
        super().__init__(self.message)

def setup_exception_handlers(app: FastAPI):
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "HTTP Exception", "detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": "Validation Error", "detail": exc.errors()},
        )

    @app.exception_handler(ExternalAPIException)
    async def external_api_exception_handler(request: Request, exc: ExternalAPIException):
        logger.error(f"{exc.provider} API Error: {exc.message} (Status: {exc.status_code})")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "External Service Error",
                "provider": exc.provider,
                "detail": exc.message
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled Server Exception")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": "An unexpected error occurred. Please try again later."},
        )
