from pydantic import BaseModel
from datetime import datetime
# 걸음 수
class StepDTO(BaseModel):
    count: int
    start_time: datetime
    end_time: datetime

# 심박수
class HeartRateDTO(BaseModel):
    bpm: float
    time: datetime

# 거리
class DistanceDTO(BaseModel):
    distance: float
    start_time: datetime
    end_time: datetime

# 칼로리
class CaloriesDTO(BaseModel):
    energy_kcal: float
    start_time: datetime
    end_time: datetime

# 수면
class SleepDTO(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime

# 운동
class ExerciseDTO(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    exercise_type: str

# 산소
class OxygenDTO(BaseModel):
    percentage: float
    time: datetime
