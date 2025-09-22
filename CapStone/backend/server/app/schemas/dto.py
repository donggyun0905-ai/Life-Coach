from pydantic import BaseModel

# 걸음 수
class StepDTO(BaseModel):
    count: int
    start_time: str
    end_time: str

# 심박수
class HeartRateDTO(BaseModel):
    bpm: float
    time: str

# 거리
class DistanceDTO(BaseModel):
    distance: float
    start_time: str
    end_time: str

# 칼로리
class CaloriesDTO(BaseModel):
    energy_kcal: float
    start_time: str
    end_time: str

# 수면
class SleepDTO(BaseModel):
    title: str
    start_time: str
    end_time: str

# 운동
class ExerciseDTO(BaseModel):
    title: str
    start_time: str
    end_time: str

# 산소
class OxygenDTO(BaseModel):
    percentage: float
    time: str
