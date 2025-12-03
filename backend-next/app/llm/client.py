from langchain.chat_models import init_chat_model
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


async def invoke_model(model_name: str, conversation: list[dict], **kargs):
    model = init_chat_model(model_name, **kargs)
    return (await model.ainvoke(conversation)).content


async def invoke_prompts(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    **kargs,
):
    model = init_chat_model(model_name, **kargs)

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return (await model.ainvoke(conversation)).content


async def invoke_model_structured(
    model_name: str,
    conversation: list[dict],
    response_model: Type[T],
    **kargs,
) -> T:
    model = init_chat_model(model_name, **kargs)
    structured_model = model.with_structured_output(response_model)
    return await structured_model.ainvoke(conversation)


async def invoke_prompts_structured(
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    response_model: Type[T],
    **kargs,
) -> T:
    model = init_chat_model(model_name, **kargs)
    structured_model = model.with_structured_output(response_model)

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return await structured_model.ainvoke(conversation)
