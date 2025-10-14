from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..schemas.database import get_db
from ..models.health import *

router = APIRouter(prefix="/v1/data", tags=["data"])

# ✅ UID 리스트 조회
@router.get("/uids")
def get_uids(db: Session = Depends(get_db)):
    uids = db.query(StepData.uid).distinct().all()
    return [u[0] for u in uids]


# ✅ UID + 기간 + 타입별 데이터 조회
@router.get("/{uid}")
def get_user_data(
    uid: str,
    type: Optional[str] = Query(None, description="steps, heart_rate, distance, calories, sleep, exercise, oxygen"),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    db: Session = Depends(get_db)
):
    def filter_query(model):
        q = db.query(model).filter(model.uid == uid)
        if start:
            # start_time이 있으면 start_time 기준 필터, 없으면 time 기준
            if hasattr(model, "start_time"):
                q = q.filter(model.start_time >= start)
            elif hasattr(model, "time"):
                q = q.filter(model.time >= start)
        if end:
            if hasattr(model, "end_time"):
                q = q.filter(model.end_time <= end)
            elif hasattr(model, "time"):
                q = q.filter(model.time <= end)
        return q.all()

    type_map = {
        "steps": StepData,
        "heart_rate": HeartRateData,
        "distance": DistanceData,
        "calories": CaloriesData,
        "sleep": SleepData,
        "exercise": ExerciseData,
        "oxygen": OxygenData,
    }

    if type:
        model = type_map.get(type)
        if not model:
            return {"error": f"Invalid type: {type}"}
        data = filter_query(model)
        return {"uid": uid, "type": type, "data": data}

    # 전체 조회
    return {
        "uid": uid,
        "steps": filter_query(StepData),
        "heart_rate": filter_query(HeartRateData),
        "distance": filter_query(DistanceData),
        "calories": filter_query(CaloriesData),
        "sleep": filter_query(SleepData),
        "exercise": filter_query(ExerciseData),
        "oxygen": filter_query(OxygenData)
    }
