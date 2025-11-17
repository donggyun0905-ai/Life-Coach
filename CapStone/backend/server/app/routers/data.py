from fastapi import APIRouter, Depends, Query, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..schemas.database import get_db
from ..models.health import *
from ..models.fcm import FcmToken  # ✅ FCM 토큰 저장 모델
import requests

router = APIRouter(prefix="/v1/data", tags=["data"])

# ------------------------------
# ✅ UID 리스트 조회
# ------------------------------
@router.get("/uids")
def get_uids(db: Session = Depends(get_db)):
    """DB에 저장된 모든 UID 조회"""
    uids = db.query(StepData.uid).distinct().all()
    return [u[0] for u in uids]


# ------------------------------
# ✅ 서버 API (토큰 기반 자동조회)
# ------------------------------
@router.get("/me")
def get_my_data(
    fcm_token: str = Header(..., description="사용자의 FCM 토큰"),
    type: str = Query(..., description="steps, heart_rate, distance, calories, sleep, exercise, oxygen"),
    start_date: datetime = Query(..., description="조회 시작일 (YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="조회 종료일 (YYYY-MM-DDTHH:MM:SS)"),
    db: Session = Depends(get_db)
):
    """
    ✅ FCM 토큰을 이용해 사용자 자동 인식 후, 지정한 기간의 건강 데이터 조회
    예: 2025-10-20T00:00:00 ~ 2025-11-05T00:00:00
    """
    record = db.query(FcmToken).filter(FcmToken.token == fcm_token).first()
    if not record:
        raise HTTPException(status_code=401, detail="Invalid FCM token")
    uid = record.uid

    type_map = {
        "steps": StepData,
        "heart_rate": HeartRateData,
        "distance": DistanceData,
        "calories": CaloriesData,
        "sleep": SleepData,
        "exercise": ExerciseData,
        "oxygen": OxygenData,
    }
    model = type_map.get(type)
    if not model:
        raise HTTPException(status_code=400, detail=f"Invalid type: {type}")

    q = db.query(model).filter(model.uid == uid)
    if hasattr(model, "start_time"):
        q = q.filter(model.start_time >= start_date, model.end_time <= end_date)
    elif hasattr(model, "time"):
        q = q.filter(model.time >= start_date, model.time <= end_date)
    data = q.all()

    return {
        "uid": uid,
        "type": type,
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "record_count": len(data),
        "data": data
    }


# ------------------------------
# ✅ 모든 데이터 요약 api
# ------------------------------
@router.get("/me/summary")
def get_my_summary(
    fcm_token: str = Header(...),
    type: str = Query(..., description="steps, heart_rate"),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db)
):
    """
    🚀 원본 데이터가 너무 클 때 사용하는 Summary 조회용 API
    - steps → 총합, 평균
    - heart_rate → 평균, 최저, 최고
    """

    # 1) FCM → UID 가져오기
    record = db.query(FcmToken).filter(FcmToken.token == fcm_token).first()
    if not record:
        raise HTTPException(status_code=401, detail="Invalid FCM token")
    uid = record.uid

    # 2) 원본 데이터 모델 선택
    type_map = {
        "steps": StepData,
        "heart_rate": HeartRateData,
    }
    model = type_map.get(type)
    if not model:
        raise HTTPException(status_code=400, detail=f"Invalid type: {type}")

    # 3) 기간 필터
    q = db.query(model).filter(model.uid == uid)
    if hasattr(model, "time"):
        q = q.filter(model.time >= start_date, model.time <= end_date)
    else:
        q = q.filter(model.start_time >= start_date, model.end_time <= end_date)

    data = q.all()

    # 4) Summary 계산
    if type == "steps":
        values = [d.count for d in data]
        total = sum(values)
        avg = total / len(values) if values else 0

        return {
            "uid": uid,
            "type": "steps",
            "total_steps": total,
            "average_steps": avg,
            "records": len(values)
        }

    if type == "heart_rate":
        values = [d.bpm for d in data]

        if not values:
            return {
                "uid": uid,
                "type": "heart_rate",
                "summary": "No data",
                "records": 0
            }

        return {
            "uid": uid,
            "type": "heart_rate",
            "min_bpm": min(values),
            "max_bpm": max(values),
            "avg_bpm": sum(values) / len(values),
            "records": len(values)
        }


# ------------------------------
# ✅ 개발자용 통합 함수 (외부에서도 바로 호출 가능)
# ------------------------------
BASE_URL = "https://capstone-lozi.onrender.com/v1/data/me"
AUTH_TOKEN = "Bearer capstone_token_0905"

def get_user_health_data(fcm_token: str, data_type: str, start_date: str, end_date: str):
    """
    ✅ 외부 개발자용 간편 호출 함수
    - 백엔드 내부나 노트북, 다른 서비스에서 바로 불러와 사용 가능
    - FastAPI 서버의 /v1/data/me 엔드포인트를 자동 호출함
    """
    params = {
        "type": data_type,
        "start_date": start_date,
        "end_date": end_date
    }

    response = requests.get(
        BASE_URL,
        headers={"fcm_token": fcm_token, "Authorization": AUTH_TOKEN},
        params=params
    )

    if response.status_code == 200:
        print(f"✅ [{data_type}] 데이터 조회 성공")
        return response.json()
    else:
        print(f"❌ 요청 실패 ({response.status_code}): {response.text}")
        return None
