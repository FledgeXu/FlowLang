from fastapi import APIRouter, Depends, HTTPException, status
from returns.io import IOFailure, IOSuccess
from returns.result import Failure, Success

from app.schemas import ArticleReq, ArticleResp
from app.services.article_service import (
    ArticleService,
    get_article_service,
)
from app.services.raw_article_service import RawArticleService, get_raw_article_service

router = APIRouter(prefix="/article", tags=["article"])


@router.post("/fetch", response_model=ArticleResp)
async def list_users(
    article_fetch: ArticleReq,
    raw_article_service: RawArticleService = Depends(get_raw_article_service),
    article_service: ArticleService = Depends(get_article_service),
):
    result = await raw_article_service.fetch_raw_article(article_fetch.url).bind(
        article_service.process_article
    )
    match result:
        case IOSuccess(Success(result)):
            return result
        case IOFailure(Failure(err)):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
            )
    raise RuntimeError("unreachable")
