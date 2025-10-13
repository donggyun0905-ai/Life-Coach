from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, Date, func
from ..schemas.database import Base
from sqlalchemy import UniqueConstraint
# 🚶 Steps
class StepData(Base):
    __tablename__ = "steps_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    count = Column(BigInteger, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    __table_args__ = (
        UniqueConstraint("uid", "start_time", "end_time", name="_uid_date_uc"),
    )


# ❤️ Heart Rate
class HeartRateData(Base):
    __tablename__ = "heartrates_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    bpm = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("uid", "time", name="_uid_time_hr_uc"),
    )


# 📏 Distance
class DistanceData(Base):
    __tablename__ = "distances_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    distance = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("uid", "start_time", "end_time", name="_uid_date_distance_uc"),
    )

# 🔥 Calories
class CaloriesData(Base):
    __tablename__ = "calories_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    calories_kcal = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("uid", "start_time", "end_time", name="_uid_date_calories_uc"),
    )

# 😴 Sleep
class SleepData(Base):
    __tablename__ = "sleeps_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    title = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("uid", "start_time", "end_time", name="_uid_date_sleep_uc"),
    )

# 🏃 Exercise
class ExerciseData(Base):
    __tablename__ = "exercises_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    exercise_type = Column(String(100), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("uid", "start_time", "end_time", name="_uid_date_exercise_uc"),
    )


# 🩸 Oxygen
class OxygenData(Base):
    __tablename__ = "oxygens_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    percentage = Column(Float, nullable=False)
    time = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint("uid", "time", name="_uid_time_oxygen_uc"),
    )

class DailySummary(Base):
    __tablename__ = "daily_summary"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    steps = Column(Integer, default=0)
    distance_m = Column(Float, default=0.0)
    calories_kcal = Column(Float, default=0.0)
    avg_heart_rate = Column(Float)
    sleep_minutes = Column(Integer)
    exercise_count = Column(Integer, default=0)
    avg_oxygen = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

# 테이블 생성
from ..schemas.database import Base, engine
from ..models import health
Base.metadata.create_all(bind=engine)
