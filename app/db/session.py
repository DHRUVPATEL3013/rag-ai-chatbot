"""
Database session/connection setup.
"""

# TODO:
#   engine = sqlalchemy.create_engine(settings.DATABASE_URL)
#   SessionLocal = sessionmaker(bind=engine)
#   def get_db():  # FastAPI dependency, yields a session and closes it


"""
Async PostgreSQL database configuration.

Used for:
- Chat history
- Feedback
- Admin review queue
- Popular queries
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async database session.
    """

    async with AsyncSessionLocal() as session:
        yield session