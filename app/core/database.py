from collections.abc import AsyncGenerator
from functools import cache
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

# -------------------------------------------------------------------
# ORM METADATA & BASE CLASS
# -------------------------------------------------------------------
# Strict naming convention ensures Alembic migrations don't crash 
# when trying to alter or drop constraints in the future.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# -------------------------------------------------------------------
# DATABASE CREATION FACTORIES (Bulletproof & Lazy-Loaded)
# -------------------------------------------------------------------
@cache
def get_engine():
    """
    Creates and caches the async database engine.
    This safely delays reading the configuration until the app actually needs it,
    preventing any validation crashes during test suites or CI/CD pipelines.
    """
    settings = get_settings()
    
    return create_async_engine(
        settings.ASYNC_DATABASE_URL,
        pool_pre_ping=True,  # Disconnect protection
        pool_recycle=3600,   # Avoid idle timeout disconnects
        pool_size=20,        # Enhanced connection pool limits for production
        max_overflow=10,
        pool_timeout=30,
        echo=False,
    )

@cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """
    Creates and caches the async session factory.
    Uses the cached engine above to bind database operations cleanly.
    """
    return async_sessionmaker(
        bind=get_engine(),
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,  # Essential for async performance
    )


# -------------------------------------------------------------------
# FASTAPI DEPENDENCY
# -------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to inject async DB sessions into route handlers.
    Ensures safe teardown and connection release back to the pool.
    """
    session_factory = get_sessionmaker()
    
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        # The 'async with' context manager automatically handles session.close()
