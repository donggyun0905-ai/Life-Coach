# app/routers/fcm.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..schemas.database import get_db
from ..models.fcm import FcmToken
import os, json, requests

# ✅ 추가!!!
from google.auth.transport.requests import Request
from google.oauth2 import service_account

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
        db.add(FcmToken(uid=req.uid, token=req.token))
    db.commit()
    return {"ok": True}


# ================================
# 2️⃣ Silent Push 발송 (HTTP v1 방식)
# ================================
class PushRequest(BaseModel):
    uid: str

@router.post("/push")
def push_silent(req: PushRequest, db: Session = Depends(get_db)):
    # ✅ 1. DB에서 토큰 조회
    token_row = db.query(FcmToken).filter(FcmToken.uid == req.uid).first()
    if not token_row:
        raise HTTPException(status_code=404, detail="FCM token not found for uid")

    # ✅ 2. Render 환경변수에서 서비스 계정 JSON 읽기
    creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not creds_json:
        raise HTTPException(status_code=500, detail="Service account credentials not configured")

    creds_info = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )

    # ✅ 핵심 수정: google.auth.transport.requests.Request() 사용
    google_request = Request()
    credentials.refresh(google_request)
    access_token = credentials.token

    project_id = creds_info["project_id"]
    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    # ✅ 3. Silent push payload (data-only)
    payload = {
        "message": {
            "token": token_row.token,
            "data": {
                "type": "sync_trigger"
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # ✅ 4. FCM HTTP v1 요청
    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail=f"FCM v1 error: {res.text}")

    return {"ok": True}
