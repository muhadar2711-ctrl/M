from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"] # By default open for testing

    # TwelveData
    TWELVEDATA_API_KEY: Optional[str] = None
    
    # MetaTrader 5 Webhook setup
    MT5_WEBHOOK_SECRET: Optional[str] = None
    MT5_WEBHOOK_URL: Optional[str] = None

    # Twitter
    TWITTER_BEARER_TOKEN: Optional[str] = None

    # Database
    POSTGRES_URL: Optional[str] = None
    
    # Locales
    DEFAULT_TIMEZONE: str = "Asia/Makassar"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra='ignore')

settings = Settings()
