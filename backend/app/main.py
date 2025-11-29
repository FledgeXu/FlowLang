import spacy
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import article, word
from app.core.setting import SETTING

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

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(article.router)
v1_router.include_router(word.router)

app.include_router(v1_router)
