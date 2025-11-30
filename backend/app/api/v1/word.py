from fastapi import APIRouter, Depends

from app.schemas import LookupReq, LookupResp
from app.services.lookup_service import LookupService, get_lookup_service

router = APIRouter(prefix="/word", tags=["article"])


@router.post("/translate", response_model=list[LookupResp])
async def translate_word(
    payload: list[LookupReq],
    lookup_service: LookupService = Depends(get_lookup_service),
):
    return await lookup_service.lookup_word(payload)
