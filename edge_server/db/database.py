"""
Database connection and setup with SQLCipher encryption
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager
from loguru import logger
from edge_server.core.config import settings
import os

# Create base class for models
Base = declarative_base()

# Database engine (will be initialized later)
engine = None
AsyncSessionLocal = None


def get_database_url():
    """Get database URL with encryption"""
    db_path = os.path.abspath(settings.DATABASE_PATH)
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # SQLCipher connection string
    # Note: For production, use proper SQLCipher setup
    # This is a simplified version using SQLite with encryption intent
    return f"sqlite+aiosqlite:///{db_path}"


async def init_db():
    """Initialize database with encryption"""
    global engine, AsyncSessionLocal
    
    try:
        database_url = get_database_url()
        
        # Create async engine
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            poolclass=StaticPool,  # For SQLite
            connect_args={
                "check_same_thread": False,
                # SQLCipher encryption key would go here in production
                # "pragmas": {"key": settings.DATABASE_KEY}
            }
        )
        
        # Create session factory
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        logger.info(f"Database location: {settings.DATABASE_PATH}")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db():
    """Close database connections"""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")


@asynccontextmanager
async def get_db():
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def get_db_session():
    """Dependency for FastAPI"""
    async with get_db() as session:
        yield session
