import uuid
from collections.abc import AsyncGenerator

from db_models import Mindmap
from fastapi import Depends
from returns.maybe import Maybe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.engine import get_async_session_maker
from repos import BaseRepository


class MindmapRepository(BaseRepository):
    async def get_or_create(self, text: str, language: str, data: dict) -> Mindmap:
        async with self.session() as session:
            stmt = (
                select(Mindmap)
                .where(Mindmap.text == text)
                .where(Mindmap.language == language)
                .where(Mindmap.data == data)
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return existing

            word = Mindmap(text=text, language=language, data=data)
            session.add(word)

            await session.flush()
            await session.refresh(word)
            return word

    async def get_by_text_and_language(
        self, text: str, language: str
    ) -> Maybe[Mindmap]:
        async with self.session() as session:
            stmt = (
                select(Mindmap)
                .where(Mindmap.text == text)
                .where(Mindmap.language == language)
            )
            result = await session.execute(stmt)
            return Maybe.from_optional(result.scalar_one_or_none())

    async def get_by_id(self, mindmap_id: uuid.UUID) -> Maybe[Mindmap]:
        async with self.session() as session:
            stmt = select(Mindmap).where(Mindmap.id == mindmap_id)
            result = await session.execute(stmt)
            return Maybe.from_optional(result.scalar_one_or_none())


async def get_minimap_repo(
    session_maker: async_sessionmaker[AsyncSession] = Depends(get_async_session_maker),
) -> AsyncGenerator[MindmapRepository, None]:
    yield MindmapRepository(session_maker)
