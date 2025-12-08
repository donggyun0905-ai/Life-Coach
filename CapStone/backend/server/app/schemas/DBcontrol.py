from ..schemas.database import SessionLocal
from sqlalchemy import text
from ..schemas.database import Base, engine
#from ..models import health
#from ..models import fcm

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


def test():
    db = SessionLocal()
    try:
        db.execute(text("""
            ALTER TABLE daily_summary
            ADD COLUMN min_heart_rate FLOAT;
            
            ALTER TABLE daily_summary
            ADD COLUMN max_heart_rate FLOAT;
        """))
        db.commit()
        print("✅ Render DB 데이터 수정 완료")
    finally:
        db.close()

def delete_record_by_id(table_name: str, record_id: int):
    """
    특정 테이블(table_name)의 특정 id(record_id) 레코드를 삭제하는 함수
    """
    db = SessionLocal()
    try:
        query = text(f"DELETE FROM {table_name} WHERE id = :rid")
        db.execute(query, {"rid": record_id})
        db.commit()
        print(f"🗑️ {table_name} 테이블에서 id={record_id} 삭제 완료")
    except Exception as e:
        print(f"❌ 삭제 오류: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    #create_tables()
    #clear_all()
    #clear_text()
    #test()
    delete_record_by_id(table_name="daily_summary", record_id=7)
    delete_record_by_id(table_name="daily_summary", record_id=8)

