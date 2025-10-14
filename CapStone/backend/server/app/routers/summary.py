from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime
from ..schemas.database import get_db
from ..models.health import DailySummary

router = APIRouter(prefix="/v1/summary", tags=["summary"])

@router.get("/{uid}")
def get_daily_summary(
    uid: str,
    start: Optional[date] = Query(None, description="조회 시작 날짜 (YYYY-MM-DD)"),
    end: Optional[date] = Query(None, description="조회 종료 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    ✅ 특정 UID의 하루 또는 기간별 DailySummary 데이터를 조회합니다.
    - start, end가 없으면 오늘 날짜 1일만 반환
    - start만 있으면 start 이후 모든 데이터 반환
    - start & end 둘 다 있으면 해당 범위만 반환
    """
    q = db.query(DailySummary).filter(DailySummary.uid == uid)

    if start:
        q = q.filter(DailySummary.date >= start)
    if end:
        q = q.filter(DailySummary.date <= end)
    if not start and not end:
        q = q.filter(DailySummary.date == date.today())

    records = q.order_by(DailySummary.date).all()

    return {
        "uid": uid,
        "count": len(records),
        "data": [
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
                "avg_oxygen": r.avg_oxygen
            } for r in records
        ]
    }
