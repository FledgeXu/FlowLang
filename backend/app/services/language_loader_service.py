from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Mapping

import polars as pl
import spacy
from spacy.language import Language


@dataclass(frozen=True)
class LanguageResource:
    model_name: str
    freq_path: str


LANGUAGE_RESOURCES: dict[str, LanguageResource] = {
    "en": LanguageResource("en_core_web_lg", "resources/english_freq.parquet"),
    "zh-cn": LanguageResource("zh_core_web_lg", "resources/chinese_freq.parquet"),
    "ja": LanguageResource("ja_core_news_lg", "resources/japanese_freq.parquet"),
}


class LanguageLoaderService:
    """Lazy loader for spaCy models and word frequency tables."""

    def __init__(
        self, resources: Mapping[str, LanguageResource] = LANGUAGE_RESOURCES
    ) -> None:
        self._resources = resources
        self._nlp_cache: dict[str, Language] = {}
        self._freq_cache: dict[str, pl.DataFrame] = {}

    def _resource(self, language: str) -> LanguageResource:
        if language not in self._resources:
            raise ValueError(f"Unsupported language: {language}")
        return self._resources[language]

    def model(self, language: str) -> Language:
        if language not in self._nlp_cache:
            resource = self._resource(language)
            self._nlp_cache[language] = spacy.load(resource.model_name)
        return self._nlp_cache[language]

    def word_freq(self, language: str) -> pl.DataFrame:
        if language not in self._freq_cache:
            resource = self._resource(language)
            self._freq_cache[language] = pl.read_parquet(resource.freq_path)
        return self._freq_cache[language]


async def get_language_loader_service() -> AsyncGenerator[LanguageLoaderService, None]:
    yield LanguageLoaderService()
