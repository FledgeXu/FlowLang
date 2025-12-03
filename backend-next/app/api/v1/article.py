from fastapi import APIRouter, Depends, HTTPException, status
from returns.io import IOFailure, IOSuccess, IO, IOResult
from returns.future import Future, FutureResult
from returns.result import Failure, Success

from app.core.settings import SETTINGS
from app.schemas import ArticleReq, ArticleResp
from app.schemas.mindmap import MindmapReq, MindmapResp
from app.services.article_service import (
    ArticleService,
    get_article_service,
)
from app.services.mindmap_service import MindmapService, get_mindmap_service
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


@router.post("/mindmap", response_model=MindmapResp)
async def translate_word(
    payload: MindmapReq,
    raw_article_service: RawArticleService = Depends(get_raw_article_service),
    mindmap_service: MindmapService = Depends(get_mindmap_service),
):
    raw_artilce = await raw_article_service.get_by_id(payload.article_id)
    result = await FutureResult.do(
        result
        for artilce in raw_artilce
        for result in await mindmap_service.get_mindmap(artilce, SETTINGS.LOCALE)
    )
    match result:
        case IOSuccess(Success(result)):
            return MindmapResp(article_id=payload.article_id, data=result.data)
        case IOFailure(Failure(err)):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err)
            )
    raise RuntimeError("unreachable")
