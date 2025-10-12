# app/routers/fcm.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas.database import get_db
from ..models.fcm import FcmToken
from pydantic import BaseModel

router = APIRouter(prefix="/v1/fcm", tags=["fcm"])

class FcmRegisterRequest(BaseModel):
    uid: str
    token: str

@router.post("/register")
def register_fcm_token(req: FcmRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(FcmToken).filter(FcmToken.uid == req.uid).first()

    if existing:
        existing.token = req.token
    else:
        new_token = FcmToken(uid=req.uid, token=req.token)
        db.add(new_token)

    db.commit()
    return {"ok": True}
