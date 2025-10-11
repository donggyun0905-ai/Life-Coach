from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from health import StepData, HeartRateData, DistanceData, CaloriesData, SleepData, ExerciseData, OxygenData
from health import DailySummary

def daily_summary(db: Session, uid: str, target_date: date):
    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

    # 🚶 총 걸음 수
    total_steps = db.query(func.sum(StepData.count))\
        .filter(StepData.uid == uid, StepData.start_time >= start_dt, StepData.end_time < end_dt)\
        .scalar() or 0

    # ❤️ 평균 심박수
    avg_hr = db.query(func.avg(HeartRateData.bpm))\
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

    # 😴 수면 시간(시간 단위)
    sleep_seconds = db.query(func.sum(func.extract('epoch', SleepData.end_time - SleepData.start_time)))\
        .filter(SleepData.uid == uid, SleepData.start_time >= start_dt, SleepData.end_time < end_dt)\
        .scalar() or 0
    sleep_hours = sleep_seconds / 3600

    # 🏃 운동 시간(시간 단위)
    exercise_seconds = db.query(func.sum(func.extract('epoch', ExerciseData.end_time - ExerciseData.start_time)))\
        .filter(ExerciseData.uid == uid, ExerciseData.start_time >= start_dt, ExerciseData.end_time < end_dt)\
        .scalar() or 0
    exercise_hours = exercise_seconds / 3600

    # 🩸 평균 산소포화도
    avg_oxygen = db.query(func.avg(OxygenData.percentage))\
        .filter(OxygenData.uid == uid, OxygenData.time >= start_dt, OxygenData.time < end_dt)\
        .scalar()

    # ✅ upsert 처리 (이미 있으면 update)
    daily = db.query(DailySummary).filter(
        DailySummary.uid == uid, DailySummary.date == target_date
    ).first()

    if daily:
        daily.steps = total_steps
        daily.avg_heart_rate = avg_hr
        daily.total_distance = total_distance
        daily.total_calories = total_calories
        daily.sleep_duration = sleep_hours
        daily.exercise_duration = exercise_hours
        daily.avg_oxygen = avg_oxygen
    else:
        daily = DailySummary(
            uid=uid,
            date=target_date,
            steps=total_steps,
            avg_heart_rate=avg_hr,
            total_distance=total_distance,
            total_calories=total_calories,
            sleep_duration=sleep_hours,
            exercise_duration=exercise_hours,
            avg_oxygen=avg_oxygen
        )
        db.add(daily)

    db.commit()
    db.refresh(daily)
    return daily
