from collections.abc import AsyncGenerator

import httpx
import spacy
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement
from fastapi import Depends
from returns.future import future_safe
from returns.io import IOResultE
from spacy.tokens.span import Span

from app.core import SETTING
from app.repos.sentence_repo import SentenceRepository, get_sentence_repo
from app.repos.word_repo import WordRepository, get_word_repo
from app.schemas import Article

LANGUAGE_MODEL = {
    "en": spacy.load("en_core_web_lg"),
    "zh-cn": spacy.load("zh_core_web_lg"),
    "ja": spacy.load("ja_core_news_lg"),
}


class ArticleService:
    def __init__(
        self,
        word_repo: WordRepository,
        sentence_repo: SentenceRepository,
    ) -> None:
        self.__word_repo = word_repo
        self.__sentence_repo = sentence_repo

    async def fetch_url(self, url: str) -> IOResultE[str]:
        article_result = self._download_article(url)
        return await article_result.bind_awaitable(self.__parse_html)

    @future_safe
    async def _download_article(self, url: str) -> Article:
        async with httpx.AsyncClient(timeout=SETTING.TIMEOUT_TIME) as client:
            r = await client.get(url)
            r.raise_for_status()
            return Article(r.text)

    async def __parse_html(self, article: Article) -> str:
        nlp = LANGUAGE_MODEL[article.language]
        raw_html = article.content

        soup = BeautifulSoup(raw_html, "lxml")
        stack: list[PageElement] = [soup]

        while stack:
            node = stack.pop()

            if isinstance(node, (Tag, BeautifulSoup)):
                if self.__should_skip_node(node):
                    continue

                children = list(node.children)
                for child in reversed(children):
                    stack.append(child)
                continue

            if isinstance(node, NavigableString):
                await self.__tokenize_text_node(node, soup, nlp)
                continue

        return str(soup)

    @staticmethod
    def __should_skip_node(node: Tag | BeautifulSoup) -> bool:
        """Return True when we do not want to tokenize inside this element."""
        return node.name in {"pre"}

    async def __render_sentence(self, sent: Span, soup: BeautifulSoup):
        s = await self.__sentence_repo.get_or_create(sent.text.strip())
        sent_id = s.id.hex

        sent_span = soup.new_tag("span", attrs={"class": "sent", "id": sent_id})
        has_valid_word = False

        for token in sent:
            text = token.text
            if not text:
                continue

            w = await self.__word_repo.get_or_create(text.strip())
            word_id = w.id.hex

            if self.__is_word_token(token):
                has_valid_word = True
                word_span = soup.new_tag(
                    "span",
                    attrs={
                        "class": "word",
                        "id": word_id,
                    },
                )
                word_span.string = text
                sent_span.append(word_span)
            else:
                sent_span.append(soup.new_string(text))

            if token.whitespace_:
                sent_span.append(soup.new_string(token.whitespace_))

        if has_valid_word:
            return sent_span

        plain_text = "".join(tok.text_with_ws for tok in sent)
        return soup.new_string(plain_text)

    @staticmethod
    def __is_word_token(token) -> bool:
        is_number_word = token.pos_ == "NUM" and not token.like_num

        return (
            (token.is_alpha or is_number_word)
            and not token.is_space
            and not token.is_punct
            and not token.like_url
            and not token.like_email
            and not token.text.isdigit()
        )

    async def __tokenize_text_node(
        self, node: NavigableString, soup: BeautifulSoup, nlp
    ) -> None:
        parent = node.parent
        if parent is None:
            return

        raw_text = str(node)
        if raw_text.strip() == "":
            return

        doc = nlp(raw_text)
        new_nodes = [await self.__render_sentence(sent, soup) for sent in doc.sents]

        for new in reversed(new_nodes):
            node.insert_after(new)

        node.extract()


async def get_article_service(
    word_repo: WordRepository = Depends(get_word_repo),
    sentence_repo: SentenceRepository = Depends(get_sentence_repo),
) -> AsyncGenerator[ArticleService, None]:
    yield ArticleService(word_repo, sentence_repo)
