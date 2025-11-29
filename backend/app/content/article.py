import json
from functools import cached_property

from bs4 import BeautifulSoup
from langdetect import detect
from trafilatura import extract


class Article:
    def __init__(self, raw_html: str) -> None:
        self.__raw_html = raw_html

    @cached_property
    def full_html(self) -> str:
        if (
            result := extract(
                self.__raw_html,
                output_format="html",
                include_formatting=True,
                include_links=False,
                include_images=False,
                with_metadata=False,
                include_comments=False,
                include_tables=False,
            )
        ) is None:
            raise ValueError("Failed to extract HTML content from raw input.")
        return result

    @cached_property
    def plain_text(self) -> str:
        return BeautifulSoup(self.full_html, "lxml").get_text(
            separator="\n", strip=True
        )

    @cached_property
    def content(self) -> str:
        soup = BeautifulSoup(
            str(
                self.full_html,
            ),
            "lxml",
        )
        body = soup.body
        if body is None:
            raise ValueError("Failed to extract HTML content from raw input.")

        inner_html = body.decode_contents()

        content_soup = BeautifulSoup(inner_html, "lxml")

        first_h1 = content_soup.find("h1")
        if first_h1:
            first_h1.decompose()

        return str(content_soup)

    @cached_property
    def language(self) -> str:
        return detect(self.plain_text)

    @cached_property
    def metadata(self) -> dict:
        if (
            result := extract(
                self.__raw_html,
                output_format="json",
                include_formatting=False,
                include_links=False,
                include_images=False,
                with_metadata=True,
                include_comments=False,
                include_tables=False,
            )
        ) is None:
            raise ValueError("Failed to extract json content from raw input.")
        return json.loads(result)

    @cached_property
    def site_name(self) -> str:
        return self.metadata["sitename"]

    @cached_property
    def title(self) -> str:
        return self.metadata["title"]

    @cached_property
    def author(self) -> str:
        return self.metadata["author"]

    @cached_property
    def date(self) -> str:
        return self.metadata["date"]

    @cached_property
    def url(self) -> str:
        return self.metadata["source"]

    @cached_property
    def hostname(self) -> str:
        return self.metadata["source-hostname"]

    @cached_property
    def description(self) -> str:
        return self.metadata["excerpt"]

    @cached_property
    def fingerprint(self) -> str:
        return self.metadata["fingerprint"]
