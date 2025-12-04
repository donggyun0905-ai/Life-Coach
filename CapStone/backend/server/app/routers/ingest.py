from fastapi import APIRouter, Depends, HTTPException, Security, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import date
import os, shutil

from ..models.health import (
    StepData, HeartRateData, DistanceData, CaloriesData,
    SleepData, ExerciseData, OxygenData, DailySummary
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

    if data:
        if data:
            from ..models.daliy_sum import daily_summary
            processed = set()
            for item in data:
                d = item.start_time.date()
                key = (item.uid, d)
                if key not in processed:
                    daily_summary(db, item.uid, d)
                    processed.add(key)

    return {"ok": True}


def update_daily_heart_summary(db: Session, uid: str, target_date: date):
    records = (
        db.query(HeartRateData)
        .filter(
            HeartRateData.uid == uid,
            HeartRateData.time >= f"{target_date} 00:00:00",
            HeartRateData.time <= f"{target_date} 23:59:59"
        )
        .all()
    )

    if not records:
        return

    bpm_values = [r.bpm for r in records]
    avg_bpm = sum(bpm_values) / len(bpm_values)
    max_bpm = max(bpm_values)
    min_bpm = min(bpm_values)

    summary = (
        db.query(DailySummary)
        .filter(DailySummary.uid == uid, DailySummary.date == target_date)
        .first()
    )

    if summary:
        summary.avg_heart_rate = avg_bpm  # ✅ 여기선 평균만 저장 (원하면 min/max 컬럼도 추가 가능)
    else:
        summary = DailySummary(
            uid=uid,
            date=target_date,
            avg_heart_rate=avg_bpm
        )
        db.add(summary)

    db.commit()
    print(f"🫀 {uid} {target_date} 심박수 집계 완료 → 평균: {avg_bpm:.2f}, 최대: {max_bpm}, 최소: {min_bpm}")


# ❤️ Heart Rate - ✅ 중복방지 + 하루 요약 반영
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

    if data:
        uid = data[0].uid
        today = data[0].time.date()
        update_daily_heart_summary(db, uid, today)

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
    if data:
        from ..models.daliy_sum import daily_summary
        processed = set()
        for item in data:
            d = item.start_time.date()
            key = (item.uid, d)
            if key not in processed:
                daily_summary(db, item.uid, d)
                processed.add(key)
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
    if data:
        from ..models.daliy_sum import daily_summary
        processed = set()
        for item in data:
            d = item.start_time.date()
            key = (item.uid, d)
            if key not in processed:
                daily_summary(db, item.uid, d)
                processed.add(key)

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
    if data:
        from ..models.daliy_sum import daily_summary
        processed = set()
        for item in data:
            d = item.end_time.date()  # 수면은 “끝난 날짜” 기준
            key = (item.uid, d)
            if key not in processed:
                daily_summary(db, item.uid, d)
                processed.add(key)

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
    if data:
        from ..models.daliy_sum import daily_summary
        processed = set()
        for item in data:
            d = item.start_time.date()
            key = (item.uid, d)
            if key not in processed:
                daily_summary(db, item.uid, d)
                processed.add(key)

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
    if data:
        from ..models.daliy_sum import daily_summary
        processed = set()
        for item in data:
            d = item.time.date()
            key = (item.uid, d)
            if key not in processed:
                daily_summary(db, item.uid, d)
                processed.add(key)

    return {"ok": True}

#-----------------------------------------------------알약 api
@router.post("/pill_image")
async def upload_pill_image(file: UploadFile = File(...)):
    os.makedirs("uploads/pills", exist_ok=True)
    save_path = f"uploads/pills/{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 딥러닝 처리 (백엔드 담당)
    #result = run_pill_model(save_path)

    return {
        "status": "ok",
        "image": save_path,
        #"pill_name": result.name,
        #"description": result.description
    }