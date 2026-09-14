# -*- coding: utf-8 -*-
"""
프론트/앱 없이 DB에 직접 테스트용 건강 데이터를 채워 넣는 스크립트.

사용법 (server 디렉터리에서):
    .venv\\Scripts\\python.exe seed_test_data.py

기본값으로 app/schemas/database.py 의 DATABASE_URL(로컬 SQLite, local_health.db)에 씁니다.
Render Postgres에 넣고 싶으면 실행 전에:
    set DATABASE_URL=postgresql://... (PowerShell: $env:DATABASE_URL="postgresql://...")
"""
import random
from datetime import datetime, timedelta, date

from app.schemas.database import SessionLocal
from app.models.health import (
    StepData, HeartRateData, DistanceData, CaloriesData,
    SleepData, ExerciseData, OxygenData, DailySummary,
)

TEST_UID = "test_uid_001"
DAYS = 20  # AI 리포트가 15일/30일 데이터를 요구하므로 넉넉히 채움


def clear_existing(db, uid):
    for model in (StepData, HeartRateData, DistanceData, CaloriesData, SleepData, ExerciseData, OxygenData, DailySummary):
        db.query(model).filter(model.uid == uid).delete()
    db.commit()


def seed():
    db = SessionLocal()
    try:
        clear_existing(db, TEST_UID)

        today = date.today()

        for day_offset in range(DAYS, -1, -1):
            day = today - timedelta(days=day_offset)
            day_start = datetime.combine(day, datetime.min.time())

            steps = random.randint(2500, 8000)
            distance_m = round(steps * random.uniform(0.65, 0.78), 1)
            calories = round(1400 + steps * random.uniform(0.03, 0.05), 1)

            # 걸음: 하루를 4개 구간으로 나눠서 기록 (앱이 15분 주기로 보내는 것과 비슷한 형태)
            remaining = steps
            for i in range(4):
                seg_start = day_start + timedelta(hours=6 + i * 4)
                seg_end = seg_start + timedelta(hours=4)
                seg_steps = remaining if i == 3 else random.randint(0, remaining // 2 or 1)
                remaining -= seg_steps
                db.add(StepData(uid=TEST_UID, count=seg_steps, start_time=seg_start, end_time=seg_end))
                db.add(DistanceData(uid=TEST_UID, distance=round(seg_steps * 0.7, 1), start_time=seg_start, end_time=seg_end))
                db.add(CaloriesData(uid=TEST_UID, calories_kcal=round(calories / 4, 1), start_time=seg_start, end_time=seg_end))

            # 심박수: 하루 8회 샘플
            bpms = []
            for h in (7, 9, 11, 13, 15, 17, 19, 21):
                bpm = random.randint(62, 92)
                bpms.append(bpm)
                db.add(HeartRateData(uid=TEST_UID, bpm=bpm, time=day_start + timedelta(hours=h, minutes=random.randint(0, 59))))

            # 산소포화도: 하루 4회 샘플
            oxygens = []
            for h in (8, 12, 18, 23):
                pct = round(random.uniform(95.0, 99.0), 1)
                oxygens.append(pct)
                db.add(OxygenData(uid=TEST_UID, percentage=pct, time=day_start + timedelta(hours=h)))

            # 수면: 전날 23시~당일 기상시간
            sleep_minutes = random.randint(360, 480)
            sleep_start = day_start - timedelta(hours=1)
            sleep_end = sleep_start + timedelta(minutes=sleep_minutes)
            db.add(SleepData(uid=TEST_UID, title="Sleep Session", start_time=sleep_start, end_time=sleep_end))

            # 운동: 60% 확률로 하루 한 번
            exercise_count = 0
            if random.random() < 0.6:
                ex_start = day_start + timedelta(hours=18)
                ex_end = ex_start + timedelta(minutes=random.randint(20, 50))
                db.add(ExerciseData(uid=TEST_UID, exercise_type="WALKING", start_time=ex_start, end_time=ex_end))
                exercise_count = 1

            db.add(DailySummary(
                uid=TEST_UID,
                date=day,
                steps=steps,
                distance_m=distance_m,
                calories_kcal=calories,
                avg_heart_rate=sum(bpms) / len(bpms),
                min_heart_rate=min(bpms),
                max_heart_rate=max(bpms),
                sleep_minutes=sleep_minutes,
                exercise_count=exercise_count,
                avg_oxygen=sum(oxygens) / len(oxygens),
            ))

        db.commit()
        print(f"✅ '{TEST_UID}' 로 {DAYS + 1}일치 테스트 데이터 삽입 완료")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
