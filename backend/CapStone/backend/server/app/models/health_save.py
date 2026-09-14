from sqlalchemy.orm import Session
from ..models.health import (
    StepData, HeartRateData, DistanceData, CaloriesData,
    SleepData, ExerciseData, OxygenData
)
from ..schemas.dto import (
    StepDTO, HeartRateDTO, DistanceDTO, CaloriesDTO,
    SleepDTO, ExerciseDTO, OxygenDTO
)
from sqlalchemy import and_

# 걸음 수
# 걸음 수 ✅ (이미 적용됨)
def save_step(db: Session, record: StepDTO):
    existing = db.query(StepData).filter(
        and_(
            StepData.uid == record.uid,
            StepData.start_time == record.start_time,
            StepData.end_time == record.end_time,
        )
    ).first()
    if existing:
        existing.count = record.count
        db.commit()
        db.refresh(existing)
        return existing
    else:
        data = StepData(**record.dict())
        db.add(data)
        db.commit()
        db.refresh(data)
        return data

# 심박수 ✅ (time 기준)
def save_heartrate(db: Session, record: HeartRateDTO):
    existing = db.query(HeartRateData).filter(
        and_(
            HeartRateData.uid == record.uid,
            HeartRateData.time == record.time
        )
    ).first()
    if existing:
        existing.bpm = record.bpm
        db.commit()
        db.refresh(existing)
        return existing
    else:
        data = HeartRateData(**record.dict())
        db.add(data)
        db.commit()
        db.refresh(data)
        return data

# 거리 ✅ (start~end 기준)
def save_distance(db: Session, record: DistanceDTO):
    existing = db.query(DistanceData).filter(
        and_(
            DistanceData.uid == record.uid,
            DistanceData.start_time == record.start_time,
            DistanceData.end_time == record.end_time
        )
    ).first()
    if existing:
        existing.distance = record.distance
        db.commit()
        db.refresh(existing)
        return existing
    else:
        data = DistanceData(**record.dict())
        db.add(data)
        db.commit()
        db.refresh(data)
        return data

# 칼로리 ✅
def save_calories(db: Session, record: CaloriesDTO):
    existing = db.query(CaloriesData).filter(
        and_(
            CaloriesData.uid == record.uid,
            CaloriesData.start_time == record.start_time,
            CaloriesData.end_time == record.end_time
        )
    ).first()
    if existing:
        existing.calories_kcal = record.calories_kcal
        db.commit()
        db.refresh(existing)
        return existing
    else:
        data = CaloriesData(**record.dict())
        db.add(data)
        db.commit()
        db.refresh(data)
        return data

# 수면 ✅
def save_sleep(db: Session, record: SleepDTO):
    existing = db.query(SleepData).filter(
        and_(
            SleepData.uid == record.uid,
            SleepData.start_time == record.start_time,
            SleepData.end_time == record.end_time
        )
    ).first()
    if existing:
        existing.title = record.title
        db.commit()
        db.refresh(existing)
        return existing
    else:
        data = SleepData(**record.dict())
        db.add(data)
        db.commit()
        db.refresh(data)
        return data

# 운동 ✅
def save_exercise(db: Session, record: ExerciseDTO):
    existing = db.query(ExerciseData).filter(
        and_(
            ExerciseData.uid == record.uid,
            ExerciseData.start_time == record.start_time,
            ExerciseData.end_time == record.end_time
        )
    ).first()
    if existing:
        existing.exercise_type = record.exercise_type
        db.commit()
        db.refresh(existing)
        return existing
    else:
        data = ExerciseData(**record.dict())
        db.add(data)
        db.commit()
        db.refresh(data)
        return data

# 산소 ✅ (time 기준)
def save_oxygen(db: Session, record: OxygenDTO):
    existing = db.query(OxygenData).filter(
        and_(
            OxygenData.uid == record.uid,
            OxygenData.time == record.time
        )
    ).first()
    if existing:
        existing.percentage = record.percentage
        db.commit()
        db.refresh(existing)
        return existing
    else:
        data = OxygenData(**record.dict())
        db.add(data)
        db.commit()
        db.refresh(data)
        return data