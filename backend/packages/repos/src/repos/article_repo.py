import uuid

from db_models import Article
from returns.maybe import Maybe
from sqlalchemy import select

from repos import BaseRepository


class ArticleRepository(BaseRepository):
    async def get_or_create(
        self,
        *,
        url: str,
        raw_html: str,
        clean_html: str,
        language: str,
        site_name: str,
        title: str,
        date: str,
        hostname: str,
        description: str,
        fingerprint: str,
    ) -> Article:
        async with self.session() as session:
            stmt = (
                select(Article)
                .where(Article.url == url)
                .where(Article.raw_html == raw_html)
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                return existing

            word = Article(
                url=url,
                raw_html=raw_html,
                clean_html=clean_html,
                language=language,
                site_name=site_name,
                title=title,
                date=date,
                hostname=hostname,
                description=description,
                fingerprint=fingerprint,
            )
            session.add(word)

            await session.flush()
            await session.refresh(word)
            return word

    async def get_by_id(self, article_id: uuid.UUID) -> Maybe[Article]:
        async with self.session() as session:
            stmt = select(Article).where(Article.id == article_id)
            result = await session.execute(stmt)
            return Maybe.from_optional(result.scalar_one_or_none())
