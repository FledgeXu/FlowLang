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
- Keep the output short: ideally around 10 tokens or fewer.
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
        word_repo: WordRepository,
        sentence_repo: SentenceRepository,
        word_lookup_repo: WordLookupRepository,
    ) -> None:
        self.__word_repo = word_repo
        self.__sentence_repo = sentence_repo
        self.__word_lookup_repo = word_lookup_repo

    async def lookup_word(self, lookups: list[LookupReq]) -> list[LookupResp]:
        result = dict()
        coros = list()
        for idx, lookup in enumerate(lookups):
            # fetch_result = await self.__word_lookup_repo.get_by_sentence_and_word(
            #     lookup.sentence_id, lookup.word_id
            # )
            # fetch_result = fetch_result.value_or(None)
            # print(fetch_result)
            # if fetch_result is not None:
            #     result[idx] = LookupResp(word_id=lookup.word_id, text=fetch_result.text)
            # else:
            coros.append(self.__look_req(idx, lookup))

        for idx, lookup, text in await asyncio.gather(*coros):
            result[idx] = LookupResp(word_id=lookup.word_id, text=text)

        return [result[k] for k in sorted(result.keys())]

    async def __look_req(
        self, idx: int, lookup: LookupReq
    ) -> tuple[int, LookupReq, str | None]:
        print(lookup)
        match await FutureResult.do(
            value
            for sentence in await self.__sentence_repo.get_by_id(lookup.sentence_id)
            for word in await self.__word_repo.get_by_id(lookup.word_id)
            for value in await lookup_word(sentence.text, word.text)
        ):
            case IOResult(Success(text)):
                return idx, lookup, text
            case IOResult(Failure(err)) | IOFailure(err):
                logger.error(err)
                return idx, lookup, None
            case _:
                return idx, lookup, None


async def get_lookup_service(
    word_repo: WordRepository = Depends(get_word_repo),
    sentence_repo: SentenceRepository = Depends(get_sentence_repo),
    word_lookup_repo: WordLookupRepository = Depends(get_word_lookup_repo),
) -> AsyncGenerator[LookupService, None]:
    yield LookupService(word_repo, sentence_repo, word_lookup_repo)
