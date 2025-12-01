from collections.abc import AsyncGenerator

import httpx
import polars as pl
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString, PageElement
from fastapi import Depends
from returns.future import future_safe
from returns.io import IOResultE
from spacy.language import Language
from spacy.tokens.span import Span
from spacy.tokens.token import Token

from app import nlp_utils
from app.content import Article
from app.core import SETTING
from app.repos.sentence_repo import SentenceRepository, get_sentence_repo
from app.repos.word_repo import WordRepository, get_word_repo

from app.schemas import ArticleResp
from .language_loader_service import LanguageLoaderService, get_language_loader_service


class ArticleService:
    def __init__(
        self,
        word_repo: WordRepository,
        sentence_repo: SentenceRepository,
        language_loader: LanguageLoaderService,
    ) -> None:
        self.__word_repo = word_repo
        self.__sentence_repo = sentence_repo
        self.__language_loader = language_loader

    async def fetch_url(self, url: str) -> IOResultE[ArticleResp]:
        article_result = self.__download_article(url)
        artilce_wrap = await article_result
        raw_html_wrap = await article_result.bind_awaitable(self.__parse_html)
        return IOResultE.do(
            ArticleResp(
                title=artilce.title,
                author=artilce.author,
                lang=artilce.language,
                raw_html=raw_html,
            )
            for artilce in artilce_wrap
            for raw_html in raw_html_wrap
        )

    @future_safe
    async def __download_article(self, url: str) -> Article:
        async with httpx.AsyncClient(timeout=SETTING.TIMEOUT_TIME) as client:
            r = await client.get(url)
            r.raise_for_status()
            return Article(r.text)

    async def __parse_html(self, article: Article) -> str:
        nlp = self.__language_loader.model(article.language)
        hard_words = set(self.__get_hard_words(nlp, article))

        soup = BeautifulSoup(article.content, "lxml")
        await self.__tokenize_dom(soup, nlp, hard_words, article.language)

        body = soup.body
        if body is None:
            return str(soup)

        return body.decode_contents()

    def __get_hard_words(
        self, nlp: Language, article: Article, k: float = 1
    ) -> list[str]:
        language = article.language
        word_freq = self.__language_loader.word_freq(language)

        lemmas = [
            nlp_utils.lemma_of_word(token, language)
            for token in nlp(article.plain_text)
        ]

        df = word_freq.filter(pl.col("word").is_in(lemmas))
        if df.height == 0:
            return []

        mean, std = df.select(
            pl.col("log_score").mean().alias("mean"),
            pl.col("log_score").std().alias("std"),
        ).row(0)

        std = std or 0
        threshold = mean + k * std

        return df.filter(pl.col("log_score") > threshold).get_column("word").to_list()

    async def __tokenize_dom(
        self,
        soup: BeautifulSoup,
        nlp: Language,
        hard_words: set[str],
        language: str,
    ) -> None:
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
                await self.__tokenize_text_node(node, soup, nlp, hard_words, language)

    @staticmethod
    def __should_skip_node(node: Tag | BeautifulSoup) -> bool:
        """Return True when we do not want to tokenize inside this element."""
        return node.name in {"pre"}

    async def __tokenize_text_node(
        self,
        node: NavigableString,
        soup: BeautifulSoup,
        nlp: Language,
        hard_words: set[str],
        language: str,
    ) -> None:
        parent = node.parent
        if parent is None:
            return

        raw_text = str(node)
        if raw_text.strip() == "":
            return

        doc = nlp(raw_text)
        new_nodes = [
            await self.__render_sentence(sent, soup, hard_words, language)
            for sent in doc.sents
        ]

        for new in reversed(new_nodes):
            node.insert_after(new)

        node.extract()

    async def __render_sentence(
        self, sent: Span, soup: BeautifulSoup, hard_words: set[str], language: str
    ):
        sentence = await self.__sentence_repo.get_or_create(sent.text.strip())
        sent_span = soup.new_tag(
            "span", attrs={"class": "sent", "sent-id": str(sentence.id)}
        )
        has_valid_word = False

        for token in sent:
            text = token.text
            if not text:
                continue

            if self.__is_word_token(token):
                word_node = await self.__build_word_node(
                    token, soup, hard_words, language
                )
                has_valid_word = True
                sent_span.append(word_node)
            else:
                sent_span.append(soup.new_string(text))

            self.__append_whitespace(sent_span, soup, token)

        if has_valid_word:
            return sent_span

        plain_text = "".join(tok.text_with_ws for tok in sent)
        return soup.new_string(plain_text)

    async def __build_word_node(
        self,
        token: Token,
        soup: BeautifulSoup,
        hard_words: set[str],
        language: str,
    ) -> Tag:
        word = await self.__word_repo.get_or_create(token.text.strip())
        lemma = nlp_utils.lemma_of_word(token, language)

        word_span = soup.new_tag(
            "span",
            attrs={"word-id": str(word.id)},
        )

        if lemma in hard_words:
            word_span["class"] = "word hard-word"
        else:
            word_span["class"] = "word"
        word_span.string = token.text
        return word_span

    @staticmethod
    def __append_whitespace(container: Tag, soup: BeautifulSoup, token: Token) -> None:
        if token.whitespace_:
            container.append(soup.new_string(token.whitespace_))

    @staticmethod
    def __is_word_token(token: Token) -> bool:
        is_number_word = token.pos_ == "NUM" and not token.like_num

        return (
            (token.is_alpha or is_number_word)
            and not token.is_space
            and not token.is_punct
            and not token.like_url
            and not token.like_email
            and not token.text.isdigit()
        )


async def get_article_service(
    word_repo: WordRepository = Depends(get_word_repo),
    sentence_repo: SentenceRepository = Depends(get_sentence_repo),
    language_loader_service: LanguageLoaderService = Depends(
        get_language_loader_service
    ),
) -> AsyncGenerator[ArticleService, None]:
    yield ArticleService(word_repo, sentence_repo, language_loader_service)
