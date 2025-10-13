from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import date

from ..models.health import (
    StepData, HeartRateData, DistanceData, CaloriesData,
    SleepData, ExerciseData, OxygenData
)
from ..schemas.dto import (
    StepDTO, HeartRateDTO, DistanceDTO, CaloriesDTO,
    SleepDTO, ExerciseDTO, OxygenDTO
)
from ..schemas.database import get_db

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])

API_TOKEN = "capstone_token_0905"
security = HTTPBearer()

def check_auth(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.scheme.lower() != "bearer" or credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


# 🚶 Steps - ✅ Upsert 적용 완료
@router.post("/steps")
def ingest_steps(data: List[StepDTO], db: Session = Depends(get_db)):
    for item in data:
        existing = (
            db.query(StepData)
            .filter(
                StepData.uid == item.uid,
                StepData.start_time == item.start_time,
                StepData.end_time == item.end_time,
            )
            .first()
        )
        if existing:
            existing.count = item.count
        else:
            db.add(StepData(**item.dict()))
    db.commit()
    return {"ok": True}


# ❤️ Heart Rate
@router.post("/heartrate")
def ingest_heartrates(data: List[HeartRateDTO], db: Session = Depends(get_db)):
    for item in data:
        existing = (
            db.query(HeartRateData)
            .filter(
                HeartRateData.uid == item.uid,
                HeartRateData.time == item.time
            )
            .first()
        )
        if existing:
            existing.bpm = item.bpm
        else:
            db.add(HeartRateData(**item.dict()))
    db.commit()
    return {"ok": True}


# 📏 Distance
@router.post("/distance")
def ingest_distance(data: List[DistanceDTO], db: Session = Depends(get_db)):
    for item in data:
        existing = (
            db.query(DistanceData)
            .filter(
                DistanceData.uid == item.uid,
                DistanceData.start_time == item.start_time,
                DistanceData.end_time == item.end_time,
            )
            .first()
        )
        if existing:
            existing.distance = item.distance
        else:
            db.add(DistanceData(**item.dict()))
    db.commit()
    return {"ok": True}


# 🔥 Calories
@router.post("/calories")
def ingest_calories(data: List[CaloriesDTO], db: Session = Depends(get_db)):
    for item in data:
        existing = (
            db.query(CaloriesData)
            .filter(
                CaloriesData.uid == item.uid,
                CaloriesData.start_time == item.start_time,
                CaloriesData.end_time == item.end_time,
            )
            .first()
        )
        if existing:
            existing.calories_kcal = item.calories_kcal
        else:
            db.add(CaloriesData(**item.dict()))
    db.commit()
    return {"ok": True}


# 😴 Sleep
@router.post("/sleep")
def ingest_sleep(data: List[SleepDTO], db: Session = Depends(get_db)):
    for item in data:
        existing = (
            db.query(SleepData)
            .filter(
                SleepData.uid == item.uid,
                SleepData.start_time == item.start_time,
                SleepData.end_time == item.end_time,
            )
            .first()
        )
        if existing:
            existing.title = item.title
        else:
            db.add(SleepData(**item.dict()))
    db.commit()
    return {"ok": True}


# 🏃 Exercise
@router.post("/exercise")
def ingest_exercise(data: List[ExerciseDTO], db: Session = Depends(get_db)):
    for item in data:
        existing = (
            db.query(ExerciseData)
            .filter(
                ExerciseData.uid == item.uid,
                ExerciseData.start_time == item.start_time,
                ExerciseData.end_time == item.end_time,
            )
            .first()
        )
        if existing:
            existing.exercise_type = item.exercise_type
        else:
            db.add(ExerciseData(**item.dict()))
    db.commit()
    return {"ok": True}


# 🩸 Oxygen
@router.post("/oxygen")
def ingest_oxygen(data: List[OxygenDTO], db: Session = Depends(get_db)):
    for item in data:
        existing = (
            db.query(OxygenData)
            .filter(
                OxygenData.uid == item.uid,
                OxygenData.time == item.time
            )
            .first()
        )
        if existing:
            existing.percentage = item.percentage
        else:
            db.add(OxygenData(**item.dict()))
    db.commit()
    return {"ok": True}
