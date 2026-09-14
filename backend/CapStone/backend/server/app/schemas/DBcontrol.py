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

def create_pill_table():
    db = SessionLocal()
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS pill_results (
                id SERIAL PRIMARY KEY,
                uid VARCHAR(255) NOT NULL,
                image_path TEXT,
                pill_name VARCHAR(255),
                appearance TEXT,
                main_usage TEXT,
                warning TEXT,
                extra_advice TEXT,
                info_json JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        db.commit()
        print("💊 pill_results 테이블 생성 완료!")
    except Exception as e:
        print("❌ pill_results 테이블 생성 오류:", e)
    finally:
        db.close()

def drop_pill_table():
    db = SessionLocal()
    try:
        db.execute(text("DROP TABLE IF EXISTS pill_results CASCADE;"))
        db.commit()
        print("🗑️ pill_result 테이블 삭제 완료")
    except Exception as e:
        print("❌ pill_result 삭제 중 오류:", e)
    finally:
        db.close()

def delete_pill_record(record_id: int):
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM pill_result WHERE id = :rid"), {"rid": record_id})
        db.commit()
        print(f"🗑️ pill_result 테이블에서 id={record_id} 삭제 완료")
    except Exception as e:
        print(f"❌ pill_result 삭제 오류: {e}")
    finally:
        db.close()
def clear_pill_table():
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE TABLE pill_result RESTART IDENTITY CASCADE;"))
        db.commit()
        print("♻️ pill_result 데이터 초기화 완료")
    except Exception as e:
        print("❌ 초기화 오류:", e)
    finally:
        db.close()

if __name__ == "__main__":
    # 기존 기능
    # create_tables()
    # clear_all()
    # clear_text()
    # test()
    # delete_record_by_id("daily_summary", 7)

    # pill 테이블 관련
    #drop_pill_table()
    create_pill_table()
    #clear_pill_table()
    #delete_pill_record(1)

