# app/routers/fcm.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas.database import get_db
from ..models.fcm import FcmToken

router = APIRouter(prefix="/v1/fcm", tags=["fcm"])

@router.post("/register")
def register_fcm_token(uid: str, token: str, db: Session = Depends(get_db)):
    existing = db.query(FcmToken).filter(FcmToken.uid == uid).first()

    if existing:
        existing.token = token
    else:
        new_token = FcmToken(uid=uid, token=token)
        db.add(new_token)

    db.commit()
    return {"ok": True}
