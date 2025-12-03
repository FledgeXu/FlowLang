from collections.abc import AsyncGenerator
from returns.maybe import Maybe
from uuid import UUID

import httpx
from fastapi import Depends
from returns.future import future_safe

from app.core.settings import SETTINGS
from app.models.base import RawArticle
from app.repos.raw_article_repo import RawArticleRepository, get_raw_article_repo


class RawArticleService:
    def __init__(self, raw_article_repo: RawArticleRepository) -> None:
        self.__raw_article_repo = raw_article_repo

    async def get_or_create(self, url: str, raw_html: str) -> RawArticle:
        return await self.__raw_article_repo.get_or_create(url, raw_html)

    @future_safe
    async def fetch_raw_article(self, url: str) -> RawArticle:
        async with httpx.AsyncClient(timeout=SETTINGS.TIMEOUT_TIME) as client:
            r = await client.get(url)
            r.raise_for_status()
            return await self.get_or_create(url=url, raw_html=r.text)

    async def get_by_id(self, raw_article_id: UUID) -> Maybe[RawArticle]:
        return await self.__raw_article_repo.get_by_id(raw_article_id)


async def get_raw_article_service(
    raw_article_repo: RawArticleRepository = Depends(get_raw_article_repo),
) -> AsyncGenerator[RawArticleService, None]:
    yield RawArticleService(raw_article_repo)
