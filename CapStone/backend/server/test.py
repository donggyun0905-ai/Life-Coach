from app.schemas.database import Base, engine
from app.models import health

print("📌 PostgreSQL에 테이블 생성 시작...")
Base.metadata.create_all(bind=engine)
print("✅ 테이블 생성 완료")