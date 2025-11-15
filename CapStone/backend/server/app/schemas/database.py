# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import Session
import os

DATABASE_URL = "postgresql://health_data_v3k6_user:x1PGAdc6e3SJNgjy9oiVMafzCbAebpic@dpg-d37b2jer433s73ejgaeg-a.singapore-postgres.render.com/health_data_v3k6"
engine = create_engine(DATABASE_URL,connect_args={"client_encoding": "utf8"})

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
