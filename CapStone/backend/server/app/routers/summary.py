from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..schemas.database import get_db
from ..models.health import DailySummary
from ..models.open_Ai import run_open_ai_health_predict

router = APIRouter(prefix="/v1/predict", tags=["predict"])


@router.get("/health/{uid}")
def predict_health(uid: str, db: Session = Depends(get_db)):
    """
    ✅ 최근 15일 건강데이터를 불러와 Gemini(Google AI)로
       15일 후 건강 점수 및 한 줄 조언을 예측하는 API
    """

    # 🔹 오늘 기준 15일 전 ~ 오늘까지 데이터 범위 설정
    end = date.today()
    start = end - timedelta(days=15)

    # 🔹 DB에서 uid 일치 + 기간 내 데이터 조회
    q = db.query(DailySummary).filter(DailySummary.uid == uid)
    q = q.filter(DailySummary.date >= start)
    q = q.filter(DailySummary.date <= end)
    records = q.order_by(DailySummary.date).all()

    # 🔹 데이터가 없으면 예외 처리
    if not records:
        return {
            "uid": uid,
            "message": "❌ 최근 15일 건강 데이터가 없습니다.",
            "start_date": start,
            "end_date": end
        }

    # 🔹 Gemini로 넘길 데이터 형태로 변환
    health_data = [
        {
            "date": r.date.isoformat(),
            "steps": r.steps,
            "sleep_minutes": r.sleep_minutes,
            "avg_heart_rate": r.avg_heart_rate,
            "calories_kcal": r.calories_kcal,
            "avg_oxygen": r.avg_oxygen
        }
        for r in records
    ]

    # 🔹 Gemini 모델로 예측 수행
    try:
        prediction = run_open_ai_health_predict(1, health_data)
    except Exception as e:
        return {
            "uid": uid,
            "message": f"❌ AI 예측 중 오류 발생: {str(e)}",
            "data_count": len(health_data)
        }

    # 🔹 결과 반환
    return {
        "uid": uid,
        "start_date": start,
        "end_date": end,
        "data_count": len(health_data),
        "prediction": prediction
    }




'''
# 하루 요약 데이터 입력방법
# ✅ [걸음 수 데이터 삽입 예시]
# - 날짜: 2025-10-14, uid: test-uid-1234
# - 하루 데이터(00:00~23:59) 기준으로 Upsert 처리됨
curl -X POST "https://capstone-lozi.onrender.com/v1/ingest/steps" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer capstone_token_0905" ^
  -d "[{\"uid\":\"test-uid-1234\",\"count\":789,\"start_time\":\"2025-10-14T00:00:00\",\"end_time\":\"2025-10-14T23:59:59\"}]"

# ✅ [심박수 데이터 삽입 예시]
curl -X POST "https://capstone-lozi.onrender.com/v1/ingest/heartrate" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer capstone_token_0905" ^
  -d "[{\"uid\":\"test-uid-1234\",\"bpm\":72,\"time\":\"2025-10-14T08:45:00\"},{\"uid\":\"test-uid-1234\",\"bpm\":85,\"time\":\"2025-10-14T10:30:00\"},{\"uid\":\"test-uid-1234\",\"bpm\":66,\"time\":\"2025-10-14T22:10:00\"}]"

# ✅ [수면 데이터 삽입 예시]
curl -X POST "https://capstone-lozi.onrender.com/v1/ingest/sleep" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer capstone_token_0905" ^
  -d "[{\"uid\":\"test-uid-1234\",\"title\":\"수면\",\"start_time\":\"2025-10-13T23:30:00\",\"end_time\":\"2025-10-14T07:30:00\"}]"

# ✅ [Daily Summary 조회 (특정 UID + 특정 날짜)]
curl "https://capstone-lozi.onrender.com/v1/summary/test-uid-1234?date=2025-10-14"

# ✅ [Daily Summary 조회 (기간 조회)]
curl "https://capstone-lozi.onrender.com/v1/summary/test-uid-1234?start=2025-10-10&end=2025-10-14"
'''