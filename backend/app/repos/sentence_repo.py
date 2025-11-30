import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends
from returns.maybe import Maybe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_async_session
from app.models.base import Sentence
from app.repos import BaseRepository


class SentenceRepository(BaseRepository):
    async def get_or_create(
        self,
        text: str,
    ) -> Sentence:
        stmt = select(Sentence).where(Sentence.text == text)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        word = Sentence(text=text)
        self._session.add(word)

        await self._session.flush()
        await self._session.refresh(word)
        return word

    async def get_by_id(self, sentence_id: uuid.UUID) -> Maybe[Sentence]:
        stmt = select(Sentence).where(Sentence.id == sentence_id)
        result = await self._session.execute(stmt)
        return Maybe.from_optional(result.scalar_one_or_none())


async def get_sentence_repo(
    async_session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SentenceRepository, None]:
    yield SentenceRepository(async_session)
