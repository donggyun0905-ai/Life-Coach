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
def save_step(db: Session, record: StepDTO):
    # 오늘 하루(00:00~23:59) 기준 기존 데이터가 있는지 확인
    existing = db.query(StepData).filter(
        and_(
            StepData.uid == record.uid,
            StepData.start_time == record.start_time,
            StepData.end_time == record.end_time,
        )
    ).first()

    if existing:
        # 이미 있으면 count만 업데이트
        existing.count = record.count
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # 없으면 새로 추가
        data = StepData(**record.dict())
        db.add(data)
        db.commit()
        db.refresh(data)
        return data

# 심박수
def save_heartrate(db: Session, record: HeartRateDTO):
    data = HeartRateData(**record.dict())
    db.add(data)
    db.commit()
    db.refresh(data)
    return data

# 거리
def save_distance(db: Session, record: DistanceDTO):
    data = DistanceData(**record.dict())
    db.add(data)
    db.commit()
    db.refresh(data)
    return data

# 칼로리
def save_calories(db: Session, record: CaloriesDTO):
    data = CaloriesData(**record.dict())
    db.add(data)
    db.commit()
    db.refresh(data)
    return data

# 수면
def save_sleep(db: Session, record: SleepDTO):
    data = SleepData(**record.dict())
    db.add(data)
    db.commit()
    db.refresh(data)
    return data

# 운동
def save_exercise(db: Session, record: ExerciseDTO):
    data = ExerciseData(**record.dict())
    db.add(data)
    db.commit()
    db.refresh(data)
    return data

# 산소
def save_oxygen(db: Session, record: OxygenDTO):
    data = OxygenData(**record.dict())
    db.add(data)
    db.commit()
    db.refresh(data)
    return data
