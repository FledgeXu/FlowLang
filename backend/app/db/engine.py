from typing import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import SETTING

engine = create_async_engine(
    SETTING.DATABASE_URL,
    echo=SETTING.DEBUG_MODE,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_async_session_maker() -> AsyncIterable[async_sessionmaker[AsyncSession]]:
    yield AsyncSessionLocal
