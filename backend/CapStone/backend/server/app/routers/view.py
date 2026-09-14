# app/routers/view.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..schemas.database import get_db
from ..models import health

router = APIRouter(prefix="/v1/view", tags=["view"])

# 👣 걸음 수 조회
@router.get("/steps")
def get_steps(db: Session = Depends(get_db)):
    return db.query(health.StepData).all()

# 🧠 심박수 조회
@router.get("/heartrates")
def get_heartrates(db: Session = Depends(get_db)):
    return db.query(health.HeartRateData).all()

# 🏃 거리 조회
@router.get("/distances")
def get_distances(db: Session = Depends(get_db)):
    return db.query(health.DistanceData).all()

# 🔥 칼로리 조회
@router.get("/calories")
def get_calories(db: Session = Depends(get_db)):
    return db.query(health.CaloriesData).all()

# 😴 수면 조회
@router.get("/sleeps")
def get_sleeps(db: Session = Depends(get_db)):
    return db.query(health.SleepData).all()

# 💪 운동 조회
@router.get("/exercises")
def get_exercises(db: Session = Depends(get_db)):
    return db.query(health.ExerciseData).all()

# 🫁 산소포화도 조회
@router.get("/oxygens")
def get_oxygens(db: Session = Depends(get_db)):
    return db.query(health.OxygenData).all()
