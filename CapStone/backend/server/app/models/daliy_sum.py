from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from ..models.health import (
    StepData, HeartRateData, DistanceData, CaloriesData,
    SleepData, ExerciseData, OxygenData, DailySummary
)

def daily_summary(db: Session, uid: str, target_date: date):
    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

    # 🚶 총 걸음 수
    total_steps = db.query(func.sum(StepData.count))\
        .filter(StepData.uid == uid, StepData.start_time >= start_dt, StepData.end_time < end_dt)\
        .scalar() or 0

    # ❤️ 평균 / 최소 / 최대 심박수
    avg_hr = db.query(func.avg(HeartRateData.bpm))\
        .filter(HeartRateData.uid == uid, HeartRateData.time >= start_dt, HeartRateData.time < end_dt)\
        .scalar()

    min_hr = db.query(func.min(HeartRateData.bpm))\
        .filter(HeartRateData.uid == uid, HeartRateData.time >= start_dt, HeartRateData.time < end_dt)\
        .scalar()

    max_hr = db.query(func.max(HeartRateData.bpm))\
        .filter(HeartRateData.uid == uid, HeartRateData.time >= start_dt, HeartRateData.time < end_dt)\
        .scalar()

    # 📏 총 거리(m)
    total_distance = db.query(func.sum(DistanceData.distance))\
        .filter(DistanceData.uid == uid, DistanceData.start_time >= start_dt, DistanceData.end_time < end_dt)\
        .scalar() or 0

    # 🔥 총 칼로리(kcal)
    total_calories = db.query(func.sum(CaloriesData.calories_kcal))\
        .filter(CaloriesData.uid == uid, CaloriesData.start_time >= start_dt, CaloriesData.end_time < end_dt)\
        .scalar() or 0

    # 😴 수면 시간(분 단위)
    sleep_seconds = db.query(
        func.sum(func.extract('epoch', SleepData.end_time - SleepData.start_time))
    ).filter(
        SleepData.uid == uid,
        SleepData.end_time >= start_dt,
        SleepData.end_time < end_dt  # 👈 end_time 기준으로 하루 판정
    ).scalar() or 0

    # 🏃 운동 시간(시간 단위)
    exercise_seconds = db.query(func.sum(func.extract('epoch', ExerciseData.end_time - ExerciseData.start_time)))\
        .filter(ExerciseData.uid == uid, ExerciseData.start_time >= start_dt, ExerciseData.end_time < end_dt)\
        .scalar() or 0
    exercise_hours = exercise_seconds / 3600

    # 🩸 평균 산소포화도
    avg_oxygen = db.query(func.avg(OxygenData.percentage))\
        .filter(OxygenData.uid == uid, OxygenData.time >= start_dt, OxygenData.time < end_dt)\
        .scalar()

    # ✅ upsert 처리
    daily = db.query(DailySummary).filter(
        DailySummary.uid == uid, DailySummary.date == target_date
    ).first()

    if daily:
        daily.steps = total_steps
        daily.distance_m = total_distance
        daily.calories_kcal = total_calories
        daily.avg_heart_rate = avg_hr
        daily.min_heart_rate = min_hr
        daily.max_heart_rate = max_hr
        daily.sleep_minutes = sleep_minutes
        daily.exercise_count = int(exercise_hours)
        daily.avg_oxygen = avg_oxygen
    else:
        daily = DailySummary(
            uid=uid,
            date=target_date,
            steps=total_steps,
            distance_m=total_distance,
            calories_kcal=total_calories,
            avg_heart_rate=avg_hr,
            min_heart_rate=min_hr,
            max_heart_rate=max_hr,
            sleep_minutes=sleep_minutes,
            exercise_count=int(exercise_hours),
            avg_oxygen=avg_oxygen
        )
        db.add(daily)

    db.commit()
    db.refresh(daily)
    return daily
