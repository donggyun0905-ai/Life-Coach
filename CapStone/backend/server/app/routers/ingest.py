from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.dto import *
from ..schemas.database import SessionLocal
from ..models.health_save import *

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])
API_TOKEN = "capstone_token_0905"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_auth(auth: str | None):
    if auth != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/steps")
def ingest_steps(records: List[StepDTO], authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved_ids = []
    for record in records:
        saved = save_step(db, record)
        saved_ids.append(saved.id)
    return {"ok": True, "ids": saved_ids}

@router.post("/heartrate")
def ingest_heartrates(records: List[HeartRateDTO], authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved_ids = []
    for record in records:
        saved = save_heartrate(db, record)
        saved_ids.append(saved.id)
    return {"ok": True, "ids": saved_ids}

@router.post("/distance")
def ingest_distances(records: List[DistanceDTO], authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved_ids = []
    for record in records:
        saved = save_distance(db, record)
        saved_ids.append(saved.id)
    return {"ok": True, "ids": saved_ids}

@router.post("/calories")
def ingest_calories(records: List[CaloriesDTO], authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved_ids = []
    for record in records:
        saved = save_calories(db, record)
        saved_ids.append(saved.id)
    return {"ok": True, "ids": saved_ids}

@router.post("/sleep")
def ingest_sleeps(records: List[SleepDTO], authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved_ids = []
    for record in records:
        saved = save_sleep(db, record)
        saved_ids.append(saved.id)
    return {"ok": True, "ids": saved_ids}

@router.post("/exercise")
def ingest_exercises(records: List[ExerciseDTO], authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved_ids = []
    for record in records:
        saved = save_exercise(db, record)
        saved_ids.append(saved.id)
    return {"ok": True, "ids": saved_ids}

@router.post("/oxygen")
def ingest_oxygens(records: List[OxygenDTO], authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved_ids = []
    for record in records:
        saved = save_oxygen(db, record)
        saved_ids.append(saved.id)
    return {"ok": True, "ids": saved_ids}

