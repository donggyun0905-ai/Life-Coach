# app/models/health.py
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from ..schemas.database import Base

# 걸음 수
class StepData(Base):
    __tablename__ = "steps_data"

    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", "count", name="uq_steps"),
    )


# 심박수
class HeartRateData(Base):
    __tablename__ = "heartrates_data"

    id = Column(Integer, primary_key=True, index=True)
    bpm = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("time", "bpm", name="uq_heartrate"),
    )


# 거리
class DistanceData(Base):
    __tablename__ = "distances_data"

    id = Column(Integer, primary_key=True, index=True)
    distance = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", "distance", name="uq_distance"),
    )


# 칼로리
class CaloriesData(Base):
    __tablename__ = "calories_data"

    id = Column(Integer, primary_key=True, index=True)
    energy_kcal = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", "energy_kcal", name="uq_calories"),
    )


# 수면
class SleepData(Base):
    __tablename__ = "sleeps_data"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", "title", name="uq_sleep"),
    )


# 운동
class ExerciseData(Base):
    __tablename__ = "exercises_data"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    exercise_type = Column(String, nullable=True)  # 운동 타입 추가 가능

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", "title", name="uq_exercise"),
    )


# 산소포화도
class OxygenData(Base):
    __tablename__ = "oxygens_data"

    id = Column(Integer, primary_key=True, index=True)
    percentage = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("time", "percentage", name="uq_oxygen"),
    )
