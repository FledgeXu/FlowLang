import spacy
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import article
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
app.include_router(v1_router)


# @app.get("/", response_class=HTMLResponse)
# async def read_root(service: ArticleService = Depends(get_article_service)):
#     match await service.fetch_url(
#         "https://www.penguin.co.uk/discover/articles/why-we-read-classics-italo-calvino"
#     ):
#         case IOSuccess(Success(article)):
#             return article
#         case IOFailure(Failure(err)):
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
#             )
#         case _:
#             raise RuntimeError("unreachable")


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
