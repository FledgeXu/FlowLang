from fastapi import APIRouter, Depends, HTTPException, status
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success

from app.schemas import ArticleFetch, ArticleResp, LookUpResp, LookUpReq
from app.services.article_service import ArticleService, get_article_service

router = APIRouter(prefix="/article", tags=["article"])


@router.post("/fetch", response_model=ArticleResp)
async def list_users(
    article_fetch: ArticleFetch,
    article_service: ArticleService = Depends(get_article_service),
):
    match await article_service.fetch_url(article_fetch.url):
        case IOSuccess(Success(text)):
            return ArticleResp(text=text)
        case IOFailure(Failure(err)):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
            )
        case _:
            raise RuntimeError("unreachable")


# @router.post("/cencert_explain", response_model=list[LookUpResp])
# async def get_cencer_expain(
#     article_fetch: ArticleFetch,
#     article_service: ArticleService = Depends(get_article_service),
# ):
#     match await article_service.fetch_url(article_fetch.url):
#         case IOSuccess(Success(text)):
#             return ArticleResp(text=text)
#         case IOFailure(Failure(err)):
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
#             )
#         case _:
#             raise RuntimeError("unreachable")
