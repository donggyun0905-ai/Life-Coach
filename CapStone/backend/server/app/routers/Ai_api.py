# app/routers/ai.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta

from ..schemas.database import get_db
from ..routers.data import get_current_uid
from ..models.health import DailySummary

from ..models.open_Ai import run_open_ai_health_predict

router = APIRouter(prefix="/v1/ai", tags=["AI"])


# ================================
# 🔥 15일 건강 예측 API
# ================================
@router.get("/predict")
def predict_15days(
    uid: str = Depends(get_current_uid),
    db: Session = Depends(get_db)
):

    # 오늘 날짜
    today = date.today()
    start_day = today - timedelta(days=15)

    # 15일 summary 가져오기
    rows = (
        db.query(DailySummary)
        .filter(
            DailySummary.uid == uid,
            DailySummary.date >= start_day,
            DailySummary.date <= today
        )
        .order_by(DailySummary.date.asc())
        .all()
    )

    # AI가 원하는 포맷으로 변환
    health_data = []
    for r in rows:
        health_data.append({
            "date": r.date.isoformat(),
            "steps": r.steps,
            "distance_m": r.distance_m,
            "calories_kcal": r.calories_kcal,
            "avg_heart_rate": r.avg_heart_rate,
            "sleep_minutes": r.sleep_minutes,
            "avg_oxygen": r.avg_oxygen,
        })

    if len(health_data) < 5:
        return {
            "error": "데이터 부족",
            "message": "AI 예측을 위해 최소 5일 이상의 summary 데이터가 필요합니다.",
            "days_loaded": len(health_data)
        }

    # AI 호출
    result = run_open_ai_health_predict(
        ver=1,
        health_data=health_data
    )

    return {
        "uid": uid,
        "days_loaded": len(health_data),
        "prediction": result
    }
