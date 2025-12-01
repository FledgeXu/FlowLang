from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ArticleReq(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    url: str


class ArticleResp(BaseModel):
    model_config = ConfigDict(
        extra="forbid", alias_generator=to_camel, populate_by_name=True
    )
    title: str
    author: str
    lang: str
    raw_html: str
