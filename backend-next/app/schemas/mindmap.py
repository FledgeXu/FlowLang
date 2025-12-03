import uuid

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class MindmapReq(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    article_id: uuid.UUID


class MindmapResp(BaseModel):
    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )

    article_id: uuid.UUID
    data: dict
