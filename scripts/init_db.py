"""
Initialize PostgreSQL database tables.
"""

import asyncio

from app.db.models import Base
from app.db.session import engine


async def init_db():
    """
    Create all database tables that do not already exist.
    """

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )

    print("Database tables created successfully.")


if __name__ == "__main__":
    asyncio.run(init_db())