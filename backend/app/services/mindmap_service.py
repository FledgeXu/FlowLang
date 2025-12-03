from collections.abc import AsyncGenerator

from fastapi import Depends
from app.domain.article import Article
from app.llm.client import invoke_prompts_structured
from returns.future import future_safe
from returns.io import IOSuccess, IOResultE
from returns.maybe import Some

from app.core.settings import SETTINGS
from app.llm.schemas import MindNode
from app.models.base import Mindmap, RawArticle
from app.repos.mindmap_repo import MindmapRepository
from app.repos.word_repo import get_word_repo


class MindmapService:
    def __init__(
        self,
        mindmap_repo: MindmapRepository,
    ) -> None:
        self.__mindmap_repo = mindmap_repo

    async def get_mindmap(
        self, raw_article: RawArticle, language: str
    ) -> IOResultE[Mindmap]:
        artilce = Article(raw_article.raw_html)
        text = artilce.plain_text
        preview_result = await self.__mindmap_repo.get_by_text_and_language(
            text, language
        )
        match preview_result:
            case Some(result):
                return IOSuccess(result)
            case _:
                return await self.__fetch_mindmap(text, language)

    @future_safe
    async def __fetch_mindmap(self, text: str, language: str):
        mind_node = await self.__generate_mindmap(text, language)
        return await self.__mindmap_repo.get_or_create(
            text, language, mind_node.model_dump()
        )

    async def __generate_mindmap(self, text: str, language: str) -> MindNode:
        system_prompt = f"""
    You are a hierarchical knowledge decomposition assistant.
    Your task:
    - Read an input text.
    - Produce a structured **mindmap** that organizes the key ideas into a tree.
    - Output format MUST be a valid JSON object that follows the MindNode schema.
    - Each node must contain:
    - "text": a short phrase summarizing the concept.
    - "children": a list of subtopics.
    - Keep the structure concise but meaningful.
    - All node texts must be in the target language: {language}.
    """

        user_prompt = f"""
    Input text:
    {text}

    Generate a mindmap describing the structure of this content.
    """

        result: MindNode = await invoke_prompts_structured(
            SETTINGS.MODEL_SPEED,
            system_prompt,
            user_prompt,
            response_model=MindNode,
        )

        return result


async def get_mindmap_service(
    mindmap_repo: MindmapRepository = Depends(get_word_repo),
) -> AsyncGenerator[MindmapService, None]:
    yield MindmapService(mindmap_repo)
