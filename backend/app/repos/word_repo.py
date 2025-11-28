import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends
from returns.maybe import Maybe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_async_session
from app.models.base import Word
from app.repos import BaseRepository


class WordRepository(BaseRepository):
    async def get_or_create(
        self,
        text: str,
    ) -> Word:
        stmt = select(Word).where(Word.text == text)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        word = Word(text=text)
        self._session.add(word)

        await self._session.flush()
        await self._session.refresh(word)
        return word

    async def get_by_id(self, word_id: uuid.UUID) -> Maybe[Word]:
        stmt = select(Word).where(Word.id == word_id)
        result = await self._session.execute(stmt)
        return Maybe.from_optional(result.scalar_one_or_none())


async def get_word_repo(
    async_session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[WordRepository, None]:
    yield WordRepository(async_session)
