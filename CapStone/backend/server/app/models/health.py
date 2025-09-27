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
        UniqueConstraint("start_time", "end_time", name="uq_steps_time"),
    )

# 심박수
class HeartRateData(Base):
    __tablename__ = "heartrates_data"

    id = Column(Integer, primary_key=True, index=True)
    bpm = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("time", name="uq_heartrate_time"),
    )

# 거리
class DistanceData(Base):
    __tablename__ = "distances_data"

    id = Column(Integer, primary_key=True, index=True)
    distance = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", name="uq_distance_time"),
    )

# 칼로리
class CaloriesData(Base):
    __tablename__ = "calories_data"

    id = Column(Integer, primary_key=True, index=True)
    energy_kcal = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", name="uq_calories_time"),
    )

# 수면
class SleepData(Base):
    __tablename__ = "sleeps_data"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", name="uq_sleep_time"),
    )

# 운동
class ExerciseData(Base):
    __tablename__ = "exercises_data"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", name="uq_exercise_time"),
    )

# 산소
class OxygenData(Base):
    __tablename__ = "oxygens_data"

    id = Column(Integer, primary_key=True, index=True)
    percentage = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("time", name="uq_oxygen_time"),
    )
