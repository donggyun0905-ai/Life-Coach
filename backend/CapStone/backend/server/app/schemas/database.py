# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

# server/.env 에 DATABASE_URL을 적어두면 매번 환경변수로 안 넘겨도 자동으로 읽힘.
load_dotenv()

# .env / 환경변수로 DATABASE_URL을 안 주면 로컬 SQLite 파일로 폴백 —
# 별도 설치·비용 없이 바로 개발·테스트 가능.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local_health.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, connect_args={"client_encoding": "utf8"})

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 모델 클래스 생성ex
Base = declarative_base()

# Dependency: FastAPI에서 사용
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
