import asyncio
from collections.abc import AsyncGenerator

from fastapi import Depends
from langchain.chat_models import init_chat_model
from loguru import logger
from returns.future import FutureResult, future_safe
from returns.io import IOFailure, IOResult
from returns.result import Failure, Success

from app.core.setting import SETTING
from app.repos.sentence_repo import SentenceRepository, get_sentence_repo
from app.repos.word_lookup_repo import WordLookupRepository, get_word_lookup_repo
from app.repos.word_repo import WordRepository, get_word_repo
from app.schemas.lookup import LookupReq, LookupResp


async def invoke_cheapest_word(conversation: list[dict], **kargs):
    model = init_chat_model("gpt-5-mini", **kargs)
    return (await model.ainvoke(conversation)).content


@future_safe
async def lookup_word(sentence: str, word: str) -> str:
    conversation = [
        {
            "role": "system",
            "content": f"""
You are a translation disambiguation assistant.
Given:
- a sentence
- a target word from that sentence
- an output language code: {SETTING.LOCALE}
Task:
Provide the most accurate translation of the target word **as it is used in the sentence**, considering its contextual meaning. 
Constraints:
- Output ONLY the translation, no explanations.
- Translation must be in the language specified by {SETTING.LOCALE}.
- Keep the output short: ideally around 20 tokens or fewer.
- Do NOT translate the whole sentence; only the given word in context.""",
        },
        {
            "role": "user",
            "content": f"""
sentence: {sentence}
word: {word} 
""",
        },
    ]
    return str(await invoke_cheapest_word(conversation))


class LookupService:
    def __init__(
        self,
        word_repository: WordRepository,
        sentence_repository: SentenceRepository,
        word_lookup_repository: WordLookupRepository,
    ) -> None:
        self.__word_repository = word_repository
        self.__sentence_repository = sentence_repository
        self.__word_lookup_repository = word_lookup_repository

    async def lookup_word(self, lookup_requests: list[LookupReq]) -> list[LookupResp]:
        logger.info(
            "Received {} lookup request(s) for word explanations",
            len(lookup_requests),
        )

        lookup_coroutines = [
            self.__process_lookup_request(lookup_request)
            for lookup_request in lookup_requests
        ]

        results = await asyncio.gather(*lookup_coroutines)

        logger.info("Finished processing {} lookup request(s)", len(lookup_requests))
        return results

    async def __process_lookup_request(self, lookup_request: LookupReq) -> LookupResp:
        sentence_id = lookup_request.sentence_id
        word_id = lookup_request.word_id

        logger.debug(
            "Processing lookup request: sentence_id={}, word_id={}",
            sentence_id,
            word_id,
        )

        cached_lookup = await self.__word_lookup_repository.get_by_sentence_and_word(
            sentence_id,
            word_id,
        )
        cached_lookup = cached_lookup.value_or(None)

        if cached_lookup is not None:
            logger.debug(
                "Cache hit for sentence_id={} word_id={}",
                sentence_id,
                word_id,
            )
            return LookupResp(word_id=word_id, text=cached_lookup.text)

        logger.debug(
            "Cache miss for sentence_id={} word_id={}, fetching.",
            sentence_id,
            word_id,
        )

        match await FutureResult.do(
            definition_text
            for sentence in await self.__sentence_repository.get_by_id(sentence_id)
            for word in await self.__word_repository.get_by_id(word_id)
            for definition_text in await lookup_word(sentence.text, word.text)
        ):
            case IOResult(Success(definition_text)):
                logger.info(
                    "Successfully fetched definition for sentence_id={} word_id={}",
                    sentence_id,
                    word_id,
                )

                created_or_existing_lookup = (
                    await self.__word_lookup_repository.get_or_create(
                        sentence_id,
                        word_id,
                        definition_text,
                    )
                )
                return LookupResp(
                    word_id=word_id,
                    text=created_or_existing_lookup.text,
                )

            case IOResult(Failure(error)) | IOFailure(error):
                logger.warning(
                    "Failed to fetch definition for sentence_id={} word_id={} due to error: {}",
                    sentence_id,
                    word_id,
                    error,
                )
                return LookupResp(word_id=word_id, text=None)

            case other:
                logger.error(
                    "Unexpected lookup result for sentence_id={} word_id={}: {!r}",
                    sentence_id,
                    word_id,
                    other,
                )
                return LookupResp(word_id=word_id, text=None)


async def get_lookup_service(
    word_repo: WordRepository = Depends(get_word_repo),
    sentence_repo: SentenceRepository = Depends(get_sentence_repo),
    word_lookup_repo: WordLookupRepository = Depends(get_word_lookup_repo),
) -> AsyncGenerator[LookupService, None]:
    yield LookupService(word_repo, sentence_repo, word_lookup_repo)
