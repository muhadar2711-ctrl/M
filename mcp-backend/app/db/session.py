from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

engine = None
AsyncSessionLocal = None

if settings.POSTGRES_URL:
    try:
        # Expected format: postgresql+asyncpg://user:pass@host:port/dbname
        engine = create_async_engine(
            settings.POSTGRES_URL, 
            echo=False, 
            future=True,
            pool_pre_ping=True
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL connection: {e}")

async def get_db():
    if AsyncSessionLocal is None:
        raise Exception("Database configuration is missing (POSTGRES_URL) or failed to initialize.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
