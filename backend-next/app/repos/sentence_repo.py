import uuid
from collections.abc import AsyncGenerator

from db_models import Sentence
from fastapi import Depends
from returns.maybe import Maybe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.engine import get_async_session_maker
from app.repos import BaseRepository


class SentenceRepository(BaseRepository):
    async def get_or_create(
        self,
        text: str,
    ) -> Sentence:
        async with self.session() as session:
            stmt = select(Sentence).where(Sentence.text == text)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return existing

            word = Sentence(text=text)
            session.add(word)

            await session.flush()
            await session.refresh(word)
            return word

    async def get_by_id(self, sentence_id: uuid.UUID) -> Maybe[Sentence]:
        async with self.session() as session:
            stmt = select(Sentence).where(Sentence.id == sentence_id)
            result = await session.execute(stmt)
            return Maybe.from_optional(result.scalar_one_or_none())


async def get_sentence_repo(
    session_maker: async_sessionmaker[AsyncSession] = Depends(get_async_session_maker),
) -> AsyncGenerator[SentenceRepository, None]:
    yield SentenceRepository(session_maker)
