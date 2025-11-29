from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class LookUpReq(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    sentence_id: str
    word_id: str


class LookUpResp(BaseModel):
    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )

    word_id: str
    text: str
