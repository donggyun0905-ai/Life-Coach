from datetime import date
from ..schemas.database import SessionLocal
from ..models.daliy_sum import daily_summary  # 함수 있는 곳 import
# 만약 파일명이 daily_sum.py 라면 from app.models.daily_sum import daily_summary

db = SessionLocal()

uid = "test-uid-1234"       # 아까 curl로 넣은 UID
target_date = date(2025, 10, 14)

daily = daily_summary(db, uid, target_date)
print("✅ Daily Summary 생성 완료:", daily.__dict__)

db.close()
