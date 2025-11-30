import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends
from returns.maybe import Maybe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.engine import get_async_session_maker
from app.models.base import Word
from app.repos import BaseRepository


class WordRepository(BaseRepository):
    async def get_or_create(
        self,
        text: str,
    ) -> Word:
        async with self.session() as session:
            stmt = select(Word).where(Word.text == text)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return existing

            word = Word(text=text)
            session.add(word)

            await session.flush()
            await session.refresh(word)
            return word

    async def get_by_id(self, word_id: uuid.UUID) -> Maybe[Word]:
        async with self.session() as session:
            stmt = select(Word).where(Word.id == word_id)
            result = await session.execute(stmt)
            return Maybe.from_optional(result.scalar_one_or_none())


async def get_word_repo(
    session_maker: async_sessionmaker[AsyncSession] = Depends(get_async_session_maker),
) -> AsyncGenerator[WordRepository, None]:
    yield WordRepository(session_maker)
