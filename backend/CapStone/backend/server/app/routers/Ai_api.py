from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta

from ..schemas.database import get_db
from ..routers.data import get_current_uid
from ..models.health import DailySummary

from ..models.open_Ai import run_open_ai_full_report

router = APIRouter(prefix="/v1/ai", tags=["AI"])


@router.get("/report")
def full_ai_report(
    uid: str = Depends(get_current_uid),
    db: Session = Depends(get_db)
):
    today = date.today()

    # -------------------------------
    # ❗ 15일 요약 데이터 가져오기
    # -------------------------------
    rows15 = (
        db.query(DailySummary)
        .filter(
            DailySummary.uid == uid,
            DailySummary.date >= today - timedelta(days=15),
            DailySummary.date <= today
        )
        .order_by(DailySummary.date.asc())
        .all()
    )

    health15 = []
    for r in rows15:
        health15.append({
            "date": r.date.isoformat(),
            "steps": r.steps,
            "distance_m": r.distance_m,
            "calories_kcal": r.calories_kcal,
            "avg_heart_rate": r.avg_heart_rate,
            "sleep_minutes": r.sleep_minutes,
            "avg_oxygen": r.avg_oxygen,
        })

    if len(health15) < 5:
        return {
            "error": "데이터 부족",
            "message": "15일 예측을 위해 5일 이상 필요",
            "days_loaded": len(health15),
        }

    # -------------------------------
    # ❗ 30일 요약 데이터 가져오기
    # -------------------------------
    rows30 = (
        db.query(DailySummary)
        .filter(
            DailySummary.uid == uid,
            DailySummary.date >= today - timedelta(days=30),
            DailySummary.date <= today
        )
        .order_by(DailySummary.date.asc())
        .all()
    )

    health30 = []
    for r in rows30:
        health30.append({
            "date": r.date.isoformat(),
            "steps": r.steps,
            "distance_m": r.distance_m,
            "calories_kcal": r.calories_kcal,
            "avg_heart_rate": r.avg_heart_rate,
            "sleep_minutes": r.sleep_minutes,
            "avg_oxygen": r.avg_oxygen,
        })

    if len(health30) < 10:
        return {
            "error": "데이터 부족",
            "message": "습관 추천을 위해 10일 이상 필요",
            "days_loaded": len(health30),
        }

    # -------------------------------
    # ⏳ AI 1번 호출
    # -------------------------------
    result = run_open_ai_full_report(health15, health30)

    return {
        "uid": uid,
        "prediction": result.get("prediction"),
        "habit": result.get("habit")
    }
