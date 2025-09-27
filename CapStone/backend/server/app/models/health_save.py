from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from ..models.health import (
    StepData, HeartRateData, DistanceData, CaloriesData,
    SleepData, ExerciseData, OxygenData
)
from ..schemas.dto import (
    StepDTO, HeartRateDTO, DistanceDTO, CaloriesDTO,
    SleepDTO, ExerciseDTO, OxygenDTO
)

# 걸음 수
def save_step(db: Session, record: StepDTO):
    stmt = insert(StepData).values(**record.dict())
    stmt = stmt.on_conflict_do_update(
        index_elements=["start_time", "end_time"],  # 고유키
        set_=record.dict()
    )
    db.execute(stmt)
    db.commit()

# 심박수
def save_heartrate(db: Session, record: HeartRateDTO):
    stmt = insert(HeartRateData).values(**record.dict())
    stmt = stmt.on_conflict_do_update(
        index_elements=["time"],  # 심박수는 단일 time 기준
        set_=record.dict()
    )
    db.execute(stmt)
    db.commit()

# 거리
def save_distance(db: Session, record: DistanceDTO):
    stmt = insert(DistanceData).values(**record.dict())
    stmt = stmt.on_conflict_do_update(
        index_elements=["start_time", "end_time"],
        set_=record.dict()
    )
    db.execute(stmt)
    db.commit()

# 칼로리
def save_calories(db: Session, record: CaloriesDTO):
    stmt = insert(CaloriesData).values(**record.dict())
    stmt = stmt.on_conflict_do_update(
        index_elements=["start_time", "end_time"],
        set_=record.dict()
    )
    db.execute(stmt)
    db.commit()

# 수면
def save_sleep(db: Session, record: SleepDTO):
    stmt = insert(SleepData).values(**record.dict())
    stmt = stmt.on_conflict_do_update(
        index_elements=["start_time", "end_time"],
        set_=record.dict()
    )
    db.execute(stmt)
    db.commit()

# 운동
def save_exercise(db: Session, record: ExerciseDTO):
    stmt = insert(ExerciseData).values(**record.dict())
    stmt = stmt.on_conflict_do_update(
        index_elements=["start_time", "end_time"],
        set_=record.dict()
    )
    db.execute(stmt)
    db.commit()

# 산소
def save_oxygen(db: Session, record: OxygenDTO):
    stmt = insert(OxygenData).values(**record.dict())
    stmt = stmt.on_conflict_do_update(
        index_elements=["time"],  # 산소포화도는 단일 time 기준
        set_=record.dict()
    )
    db.execute(stmt)
    db.commit()
