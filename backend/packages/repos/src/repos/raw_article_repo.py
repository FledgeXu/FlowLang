import uuid
from collections.abc import AsyncGenerator

from db_models import RawArticle
from fastapi import Depends
from returns.maybe import Maybe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.engine import get_async_session_maker
from repos import BaseRepository


class RawArticleRepository(BaseRepository):
    async def get_or_create(self, url: str, raw_html: str) -> RawArticle:
        async with self.session() as session:
            stmt = (
                select(RawArticle)
                .where(RawArticle.url == url)
                .where(RawArticle.raw_html == raw_html)
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return existing

            word = RawArticle(url=url, raw_html=raw_html)
            session.add(word)

            await session.flush()
            await session.refresh(word)
            return word

    async def get_by_id(self, raw_article_id: uuid.UUID) -> Maybe[RawArticle]:
        async with self.session() as session:
            stmt = select(RawArticle).where(RawArticle.id == raw_article_id)
            result = await session.execute(stmt)
            return Maybe.from_optional(result.scalar_one_or_none())


async def get_raw_article_repo(
    session_maker: async_sessionmaker[AsyncSession] = Depends(get_async_session_maker),
) -> AsyncGenerator[RawArticleRepository, None]:
    yield RawArticleRepository(session_maker)
