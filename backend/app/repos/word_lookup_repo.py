import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends
from returns.maybe import Maybe
from sqlalchemy import Integer, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_async_session
from app.models.base import WordLookup
from app.repos import BaseRepository


class WordLookupRepository(BaseRepository):
    async def get_by_sentence_and_word(
        self, sentence_id: uuid.UUID, word_id: uuid.UUID
    ) -> Maybe[WordLookup]:
        stmt = (
            select(WordLookup)
            .where(WordLookup.sentence_id == sentence_id)
            .where(WordLookup.word_id == word_id)
        )
        result = await self._session.execute(stmt)
        return Maybe.from_optional(result.scalar_one_or_none())

    async def get_or_create(
        self, sentence_id: uuid.UUID, word_id: uuid.UUID, text: str
    ) -> WordLookup:
        stmt = (
            select(WordLookup)
            .where(WordLookup.sentence_id == sentence_id)
            .where(WordLookup.word_id == word_id)
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return existing

        lookup = WordLookup(sentence_id=sentence_id, word_id=word_id, text=text)
        self._session.add(lookup)

        await self._session.flush()
        await self._session.refresh(lookup)
        return lookup

    async def get_by_id(self, lookup_id: Integer) -> Maybe[WordLookup]:
        stmt = select(WordLookup).where(WordLookup.id == lookup_id)
        result = await self._session.execute(stmt)
        return Maybe.from_optional(result.scalar_one_or_none())


async def get_word_lookup_repo(
    async_session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[WordLookupRepository, None]:
    yield WordLookupRepository(async_session)
