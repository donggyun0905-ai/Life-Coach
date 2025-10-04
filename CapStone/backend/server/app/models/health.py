from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, Double
from ..schemas.database import Base

# 📝 공통: uid 컬럼 추가 (VARCHAR), 테이블명 정리 (복수형 → 단수 or 명확한 이름)

# 🚶 Steps
class StepData(Base):
    __tablename__ = "steps_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)   # ✅ 사용자 구분
    count = Column(BigInteger, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


# ❤️ Heart Rate
class HeartRateData(Base):
    __tablename__ = "heartrates_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    bpm = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


# 📏 Distance
class DistanceData(Base):
    __tablename__ = "distances_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    distance_m = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


# 🔥 Calories
class CaloriesData(Base):
    __tablename__ = "calories_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    calories_kcal = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


# 😴 Sleep
class SleepData(Base):
    __tablename__ = "sleeps_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    stage = Column(String(50), nullable=False)  # ✅ title → stage로 변경
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


# 🏃 Exercise
class ExerciseData(Base):
    __tablename__ = "exercises_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    exercise_type = Column(String(100), nullable=False)
    duration_seconds = Column(BigInteger, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


# 🩸 Oxygen
class OxygenData(Base):
    __tablename__ = "oxygens_data"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String(255), nullable=False)
    percentage = Column(Float, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)



# 테이블 생성
from ..schemas.database import Base, engine
from ..models import health
Base.metadata.create_all(bind=engine)
