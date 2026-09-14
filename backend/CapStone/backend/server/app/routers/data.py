from fastapi import APIRouter, Depends, Query, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date

from ..schemas.database import get_db
from ..models.health import (
    StepData,
    HeartRateData,
    DistanceData,
    CaloriesData,
    SleepData,
    ExerciseData,
    OxygenData,
    DailySummary,
)
from ..models.fcm import FcmToken  # uid 관리용으로 재사용

import requests

router = APIRouter(prefix="/v1/data", tags=["data"])

#api file

# =========================================
# 🔐 공통 인증: X-DEVICE-TOKEN 기반 uid 추출
# =========================================
def get_current_uid(
    x_device_token: str = Header(..., alias="X-DEVICE-TOKEN"),
    db: Session = Depends(get_db),
) -> str:
    """
    안드로이드에서 Interceptor가 보내는 X-DEVICE-TOKEN 헤더를
    인증 키이자 uid로 사용한다.
    필요하면 FcmToken 테이블에 uid를 등록해둔다.
    """
    uid = x_device_token

    # 선택: FcmToken 테이블에 uid만이라도 등록해 두기 (토큰은 빈 값)
    record = db.query(FcmToken).filter(FcmToken.uid == uid).first()
    if not record:
        record = FcmToken(uid=uid, token="")
        db.add(record)
        db.commit()
        db.refresh(record)

    return uid


# ------------------------------
# ✅ UID 리스트 조회
# ------------------------------
@router.get("/uids")
def get_uids(db: Session = Depends(get_db)):
    """DB에 저장된 모든 UID 조회"""
    uids = db.query(StepData.uid).distinct().all()
    return [u[0] for u in uids]


# ------------------------------
# ✅ 나의 원시 데이터 조회 (/me)
#    - X-DEVICE-TOKEN 기반
# ------------------------------
@router.get("/me")
def get_my_data(
    data_type: str = Query(
        ...,
        alias="type",
        description="steps, heart_rate, distance, calories, sleep, exercise, oxygen",
    ),
    start_date: datetime = Query(..., description="조회 시작일 (YYYY-MM-DDTHH:MM:SS)"),
    end_date: datetime = Query(..., description="조회 종료일 (YYYY-MM-DDTHH:MM:SS)"),
    uid: str = Depends(get_current_uid),
    db: Session = Depends(get_db),
):
    """
    ✅ X-DEVICE-TOKEN(=uid) 기반으로, 내 데이터만 기간 조회
    예: 2025-10-20T00:00:00 ~ 2025-11-05T00:00:00
    """

    type_map = {
        "steps": StepData,
        "heart_rate": HeartRateData,
        "distance": DistanceData,
        "calories": CaloriesData,
        "sleep": SleepData,
        "exercise": ExerciseData,
        "oxygen": OxygenData,
    }
    model = type_map.get(data_type)
    if not model:
        raise HTTPException(status_code=400, detail=f"Invalid type: {data_type}")

    q = db.query(model).filter(model.uid == uid)

    # start_time / end_time 이 있는 모델
    if hasattr(model, "start_time") and hasattr(model, "end_time"):
        q = q.filter(model.start_time >= start_date, model.end_time <= end_date)
    # time 만 있는 모델 (심박수, 산소 등)
    elif hasattr(model, "time"):
        q = q.filter(model.time >= start_date, model.time <= end_date)

    data = q.all()

    return {
        "uid": uid,
        "type": data_type,
        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
        "record_count": len(data),
        "data": data,
    }


# ================================
# ⭐ 나의 Summary 조회 (/me-summary)
#    - X-DEVICE-TOKEN 기반
# ================================
@router.get("/me-summary")
def get_my_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    uid: str = Depends(get_current_uid),
    db: Session = Depends(get_db),
):
    """
    ✅ 내 uid + 기간 기준으로 DailySummary 조회
    """
    rows = (
        db.query(DailySummary)
        .filter(
            DailySummary.uid == uid,
            DailySummary.date >= start_date,
            DailySummary.date <= end_date,
        )
        .all()
    )

    summary_data = [
        {
            "date": r.date,
            "steps": r.steps,
            "distance_m": r.distance_m,
            "calories_kcal": r.calories_kcal,
            "avg_heart_rate": r.avg_heart_rate,
            "min_heart_rate": r.min_heart_rate,
            "max_heart_rate": r.max_heart_rate,
            "sleep_minutes": r.sleep_minutes,
            "exercise_count": r.exercise_count,
            "avg_oxygen": r.avg_oxygen,
        }
        for r in rows
    ]

    return {
        "uid": uid,
        "start_date": start_date,
        "end_date": end_date,
        "days": len(summary_data),
        "summary": summary_data,
    }


# ================================
# ⭐ 오늘 Summary 조회 (/today-summary)
#    - Day1 목표용: 프론트/앱에서 바로 사용
# ================================
@router.get("/today-summary")
def get_today_summary(
    uid: str = Depends(get_current_uid),
    db: Session = Depends(get_db),
):
    """
    ✅ 오늘 하루(date.today()) 기준 내 DailySummary 1건 조회
    """
    today = date.today()

    r = (
        db.query(DailySummary)
        .filter(
            DailySummary.uid == uid,
            DailySummary.date == today,
        )
        .first()
    )

    if not r:
        return {
            "uid": uid,
            "date": today,
            "has_summary": False,
            "message": "No summary for today",
        }

    return {
        "uid": uid,
        "date": today,
        "has_summary": True,
        "steps": r.steps,
        "distance_m": r.distance_m,
        "calories_kcal": r.calories_kcal,
        "avg_heart_rate": r.avg_heart_rate,
        "min_heart_rate": r.min_heart_rate,
        "max_heart_rate": r.max_heart_rate,
        "sleep_minutes": r.sleep_minutes,
        "exercise_count": r.exercise_count,
        "avg_oxygen": r.avg_oxygen,
    }


# ------------------------------
# ✅ (선택) 개발자용 헬퍼 함수
#     - 외부 스크립트에서 사용 가능
# ------------------------------
BASE_URL = "https://capstone-lozi.onrender.com/v1/data/me"


def get_user_health_data(
    uid: str, data_type: str, start_date: str, end_date: str
):
    """
    ✅ 외부에서 간단하게 /v1/data/me 호출하고 싶을 때 쓰는 헬퍼
    - uid: X-DEVICE-TOKEN 과 동일한 값
    - data_type: steps / heart_rate / distance / ...
    - start_date, end_date: "YYYY-MM-DDTHH:MM:SS"
    """
    params = {
        "type": data_type,
        "start_date": start_date,
        "end_date": end_date,
    }

    response = requests.get(
        BASE_URL,
        headers={"X-DEVICE-TOKEN": uid},
        params=params,
    )

    if response.status_code == 200:
        print(f"✅ [{data_type}] 데이터 조회 성공")
        return response.json()
    else:
        print(f"❌ 요청 실패 ({response.status_code}): {response.text}")
        return None
