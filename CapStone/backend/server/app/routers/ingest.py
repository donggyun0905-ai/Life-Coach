from fastapi import APIRouter, Header, HTTPException
from ..schemas.dto import HcIngestDTO   # ← 상대 임포트로 변경 (..schemas.dto)

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])
API_TOKEN = "CHANGE_ME"

@router.post("/healthconnect")
def ingest_healthconnect(payload: HcIngestDTO, authorization: str | None = Header(None)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"ok": True, "count": len(payload.summaries)}
