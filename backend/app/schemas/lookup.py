import uuid

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class LookupReq(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    sentence_id: uuid.UUID
    word_id: uuid.UUID


class LookupResp(BaseModel):
    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )

    word_id: uuid.UUID
    text: str | None
