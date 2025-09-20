from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from ..schemas.dto import *
from ..schemas.database import SessionLocal
from ..models.health_save import *

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])
API_TOKEN = "CHANGE_ME"

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
def ingest_step(record: StepDTO, authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved = save_step(db, record)
    return {"ok": True, "id": saved.id}

@router.post("/heartrate")
def ingest_heartrate(record: HeartRateDTO, authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved = save_heartrate(db, record)
    return {"ok": True, "id": saved.id}

@router.post("/distance")
def ingest_distance(record: DistanceDTO, authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved = save_distance(db, record)
    return {"ok": True, "id": saved.id}

@router.post("/calories")
def ingest_calories(record: CaloriesDTO, authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved = save_calories(db, record)
    return {"ok": True, "id": saved.id}

@router.post("/sleep")
def ingest_sleep(record: SleepDTO, authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved = save_sleep(db, record)
    return {"ok": True, "id": saved.id}

@router.post("/exercise")
def ingest_exercise(record: ExerciseDTO, authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved = save_exercise(db, record)
    return {"ok": True, "id": saved.id}

@router.post("/oxygen")
def ingest_oxygen(record: OxygenDTO, authorization: str | None = Header(None), db: Session = Depends(get_db)):
    check_auth(authorization)
    saved = save_oxygen(db, record)
    return {"ok": True, "id": saved.id}
