# app/models/health.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 걸음 수
class StepData(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)

# 심박수
class HeartRateData(Base):
    __tablename__ = "heartrates"

    id = Column(Integer, primary_key=True, index=True)
    bpm = Column(Float, nullable=False)
    time = Column(String, nullable=False)

# 거리
class DistanceData(Base):
    __tablename__ = "distances"

    id = Column(Integer, primary_key=True, index=True)
    distance = Column(Float, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)

# 칼로리
class CaloriesData(Base):
    __tablename__ = "calories"

    id = Column(Integer, primary_key=True, index=True)
    energy_kcal = Column(Float, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)

# 수면
class SleepData(Base):
    __tablename__ = "sleeps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)

# 운동
class ExerciseData(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)

# 산소
class OxygenData(Base):
    __tablename__ = "oxygens"

    id = Column(Integer, primary_key=True, index=True)
    percentage = Column(Float, nullable=False)
    time = Column(String, nullable=False)
