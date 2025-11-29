from fastapi import APIRouter

from app.schemas import LookUpReq, LookUpResp

router = APIRouter(prefix="/word", tags=["article"])


@router.post("/translate", response_model=list[LookUpResp])
async def translate_word(payload: list[LookUpReq]):
    return [LookUpResp(word_id="6619d11755564b77aad7414d9f8032fd", text="HHH")]
