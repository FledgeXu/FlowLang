import uuid
from collections.abc import AsyncGenerator

from db_models import WordLookup
from fastapi import Depends
from returns.maybe import Maybe
from sqlalchemy import Integer, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.engine import get_async_session_maker
from app.repos import BaseRepository


class WordLookupRepository(BaseRepository):
    async def get_by_sentence_and_word(
        self, sentence_id: uuid.UUID, word_id: uuid.UUID, language: str
    ) -> Maybe[WordLookup]:
        async with self.session() as session:
            stmt = (
                select(WordLookup)
                .where(WordLookup.sentence_id == sentence_id)
                .where(WordLookup.word_id == word_id)
                .where(WordLookup.language == language)
            )
            result = await session.execute(stmt)
            return Maybe.from_optional(result.scalar_one_or_none())

    async def get_or_create(
        self, sentence_id: uuid.UUID, word_id: uuid.UUID, text: str, language: str
    ) -> WordLookup:
        async with self.session() as session:
            stmt = (
                select(WordLookup)
                .where(WordLookup.sentence_id == sentence_id)
                .where(WordLookup.word_id == word_id)
                .where(WordLookup.language == language)
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return existing

            lookup = WordLookup(
                sentence_id=sentence_id, word_id=word_id, text=text, language=language
            )
            session.add(lookup)

            await session.flush()
            await session.refresh(lookup)
            return lookup

    async def get_by_id(self, lookup_id: Integer) -> Maybe[WordLookup]:
        async with self.session() as session:
            stmt = select(WordLookup).where(WordLookup.id == lookup_id)
            result = await session.execute(stmt)
            return Maybe.from_optional(result.scalar_one_or_none())


async def get_word_lookup_repo(
    session_maker: async_sessionmaker[AsyncSession] = Depends(get_async_session_maker),
) -> AsyncGenerator[WordLookupRepository, None]:
    yield WordLookupRepository(session_maker)
