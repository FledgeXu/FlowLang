import os
from typing import AsyncIterable

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv(override=True)


engine = create_async_engine(
    os.getenv("MIGRATION_DATABASE_URL", "sqlite+aiosqlite:///../../temp.db"),
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_async_session_maker() -> AsyncIterable[async_sessionmaker[AsyncSession]]:
    yield AsyncSessionLocal
