#from database import SessionLocal
#from sqlalchemy import text

from app.schemas.database import Base, engine
from app.models import health

def clear_all():
    db = SessionLocal()
    try:
        db.execute(text("""
            DROP TABLE steps_data CASCADE;
            DROP TABLE heartrates_data CASCADE;
            DROP TABLE distances_data CASCADE;
            DROP TABLE calories_data CASCADE;
            DROP TABLE sleeps_data CASCADE;
            DROP TABLE exercises_data CASCADE;
            DROP TABLE oxygens_data CASCADE;
        """))
        db.commit()
        print("✅ Render DB 데이터 초기화 완료")
    finally:
        db.close()

def clear_text():
    db = SessionLocal()
    try:
        db.execute(text("""
            TRUNCATE TABLE steps_data RESTART IDENTITY CASCADE;
            TRUNCATE TABLE heartrates_data RESTART IDENTITY CASCADE;
            TRUNCATE TABLE distances_data RESTART IDENTITY CASCADE;
            TRUNCATE TABLE calories_data RESTART IDENTITY CASCADE;
            TRUNCATE TABLE sleeps_data RESTART IDENTITY CASCADE;
            TRUNCATE TABLE exercises_data RESTART IDENTITY CASCADE;
            TRUNCATE TABLE oxygens_data RESTART IDENTITY CASCADE;
        """))
        db.commit()
        print("✅ Render DB 데이터 초기화 완료")
    finally:
        db.close()

def create_tables():
    print("⏳ 테이블 생성 시작...")
    Base.metadata.create_all(bind=engine)
    print("✅ 테이블 생성 완료!")

if __name__ == "__main__":
    create_tables()
    #clear_all()
    #clear_text()
