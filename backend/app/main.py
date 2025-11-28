from typing import Union

import spacy
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success
from starlette.responses import HTMLResponse

from app.core.setting import SETTING
from app.services.article_service import ArticleService, get_article_service

LANGUAGE_MODEL = {
    "en": spacy.load("en_core_web_lg"),
    "zh": spacy.load("zh_core_web_lg"),
    "ja": spacy.load("ja_core_news_lg"),
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTING.ORIGIN_URLS.split("|"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def read_root(service: ArticleService = Depends(get_article_service)):
    match await service.fetch_url(
        "https://huggingface.co/blog/zh/chinese-language-blog"
    ):
        case IOSuccess(Success(article)):
            return article
        case IOFailure(Failure(err)):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
            )
        case _:
            raise RuntimeError("unreachable")


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
