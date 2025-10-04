from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..schemas.dto import (   # ✅ dto → health로 파일명 변경되어 있다면 여기도 수정
    StepDTO, HeartRateDTO, DistanceDTO, CaloriesDTO,
    SleepDTO, ExerciseDTO, OxygenDTO
)
from ..schemas.database import get_db
from ..models.health import (    # ✅ health_save → health로 정리
    StepData, HeartRateData, DistanceData, CaloriesData,
    SleepData, ExerciseData, OxygenData
)

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])

API_TOKEN = "capstone_token_0905"
security = HTTPBearer()

def check_auth(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.scheme.lower() != "bearer" or credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


# 🧱 공통 저장 함수
def save_record(db: Session, model_class, record):
    obj = model_class(**record.dict())   # ✅ uid 포함해서 그대로 언패킹
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# 🚶 Steps
@router.post("/steps")
def ingest_steps(
    records: List[StepDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_record(db, StepData, record).id for record in records]
    return {"ok": True, "ids": saved_ids}


# ❤️ Heart Rate
@router.post("/heartrate")
def ingest_heartrates(
    records: List[HeartRateDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_record(db, HeartRateData, record).id for record in records]
    return {"ok": True, "ids": saved_ids}


# 📏 Distance
@router.post("/distance")
def ingest_distances(
    records: List[DistanceDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_record(db, DistanceData, record).id for record in records]
    return {"ok": True, "ids": saved_ids}


# 🔥 Calories
@router.post("/calories")
def ingest_calories(
    records: List[CaloriesDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_record(db, CaloriesData, record).id for record in records]
    return {"ok": True, "ids": saved_ids}


# 😴 Sleep
@router.post("/sleep")
def ingest_sleeps(
    records: List[SleepDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_record(db, SleepData, record).id for record in records]
    return {"ok": True, "ids": saved_ids}


# 🏃 Exercise
@router.post("/exercise")
def ingest_exercises(
    records: List[ExerciseDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_record(db, ExerciseData, record).id for record in records]
    return {"ok": True, "ids": saved_ids}


# 🩸 Oxygen
@router.post("/oxygen")
def ingest_oxygens(
    records: List[OxygenDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    print(f"📩 oxygen {len(records)} records received")
    check_auth(credentials)
    saved_ids = [save_record(db, OxygenData, record).id for record in records]
    return {"ok": True, "ids": saved_ids}
