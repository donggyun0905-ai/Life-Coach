# app/routers/fcm.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..schemas.database import get_db
from ..models.fcm import FcmToken
import os, requests

router = APIRouter(prefix="/v1/fcm", tags=["fcm"])

# ================================
# 1️⃣ FCM 토큰 등록
# ================================
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


# ================================
# 2️⃣ Silent Push 발송
# ================================
FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY")  # ✅ Render 환경변수에 저장해둬야 함

class PushRequest(BaseModel):
    uid: str

@router.post("/push")
def push_silent(req: PushRequest, db: Session = Depends(get_db)):
    token_row = db.query(FcmToken).filter(FcmToken.uid == req.uid).first()
    if not token_row:
        raise HTTPException(status_code=404, detail="FCM token not found for uid")

    if not FCM_SERVER_KEY:
        raise HTTPException(status_code=500, detail="FCM_SERVER_KEY not configured")

    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": token_row.token,
        "priority": "high",  # 즉시 전달
        "data": {"type": "sync_trigger"}  # 앱 쪽에서 이 type을 받으면 Worker 실행
    }

    res = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, json=payload)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail=f"FCM error: {res.text}")

    return {"ok": True}
