import asyncio

from playwright.async_api import async_playwright
from repos.article_repo import ArticleRepository
from returns.result import safe

from document_ingestion.engine import AsyncSessionLocal

from .article import Article


def main() -> None:
    asyncio.run(fetch())


async def fetch():
    repo = ArticleRepository(AsyncSessionLocal)
    raw_html = await fetch_article(
        "https://www.penguin.co.uk/discover/articles/why-we-read-classics-italo-calvino"
    )
    # article_wrap = raw_html.map(lambda html: Article(html))
    article_wrap = Article(raw_html)
    await repo.get_or_create(
        url="https://www.penguin.co.uk/discover/articles/why-we-read-classics-italo-calvino",
        raw_html=raw_html,
        clean_html=article_wrap.full_html,
        language=article_wrap.language,
        site_name="",
        title=article_wrap.title,
        date=article_wrap.date,
        hostname=article_wrap.hostname,
        description=article_wrap.description,
        fingerprint=article_wrap.fingerprint,
    )


# @safe
async def fetch_article(url: str, timeout: float = 60 * 1000) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        try:
            page = await browser.new_page()
            await page.goto(url, timeout=timeout)
            await page.wait_for_load_state("networkidle", timeout=timeout)
            return await page.content()
        finally:
            await browser.close()
