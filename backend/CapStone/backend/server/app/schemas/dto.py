from pydantic import BaseModel
from datetime import datetime

# ✅ 공통 베이스
class BaseHealth(BaseModel):
    uid: str

    class Config:
        orm_mode = True


# 🚶 Steps
class StepDTO(BaseHealth):
    count: int
    start_time: datetime
    end_time: datetime


# ❤️ Heart Rate
class HeartRateDTO(BaseHealth):
    bpm: float
    time: datetime


# 📏 Distance
class DistanceDTO(BaseHealth):
    distance: float
    start_time: datetime
    end_time: datetime


# 🔥 Calories
class CaloriesDTO(BaseHealth):
    calories_kcal: float
    start_time: datetime
    end_time: datetime


# 😴 Sleep
class SleepDTO(BaseHealth):
    title: str
    start_time: datetime
    end_time: datetime


# 🏃 Exercise
class ExerciseDTO(BaseHealth):
    exercise_type: str
    start_time: datetime
    end_time: datetime


# 🩸 Oxygen
class OxygenDTO(BaseHealth):
    percentage: float
    time: datetime
