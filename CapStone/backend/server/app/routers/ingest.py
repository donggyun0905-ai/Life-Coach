from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..schemas.dto import (
    StepDTO, HeartRateDTO, DistanceDTO, CaloriesDTO,
    SleepDTO, ExerciseDTO, OxygenDTO
)
from ..schemas.database import get_db
from ..models.health_save import *

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])

API_TOKEN = "capstone_token_0905"
security = HTTPBearer()

def check_auth(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.scheme.lower() != "bearer" or credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("/steps")
def ingest_steps(
    records: List[StepDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_step(db, record).id for record in records]
    return {"ok": True, "ids": saved_ids}

@router.post("/heartrate")
def ingest_heartrates(
    records: List[HeartRateDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_heartrate(db, record).id for record in records]
    return {"ok": True, "ids": saved_ids}

@router.post("/distance")
def ingest_distances(
    records: List[DistanceDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_distance(db, record).id for record in records]
    return {"ok": True, "ids": saved_ids}

@router.post("/calories")
def ingest_calories(
    records: List[CaloriesDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_calories(db, record).id for record in records]
    return {"ok": True, "ids": saved_ids}

@router.post("/sleep")
def ingest_sleeps(
    records: List[SleepDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_sleep(db, record).id for record in records]
    return {"ok": True, "ids": saved_ids}

@router.post("/exercise")
def ingest_exercises(
    records: List[ExerciseDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    check_auth(credentials)
    saved_ids = [save_exercise(db, record).id for record in records]
    return {"ok": True, "ids": saved_ids}

@router.post("/oxygen")
def ingest_oxygens(
    records: List[OxygenDTO],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)):
    print(f"📩 oxygen {len(records)} records received")
    check_auth(credentials)
    saved_ids = [save_oxygen(db, record).id for record in records]
    return {"ok": True, "ids": saved_ids}
