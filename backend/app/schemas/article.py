from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ArticleFetch(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    url: str


class ArticleResp(BaseModel):
    model_config = ConfigDict(extra="forbid", alias_generator=to_camel)

    text: str
