# app/models/fcm.py 한번만 실행해서 table 만드는 부분 삭제해도 되지만 오류 해결을 위해 지우지는 말도록
from sqlalchemy import Column, String, DateTime, func
from ..schemas.database import Base

class FcmToken(Base):
    __tablename__ = "fcm_tokens"

    uid = Column(String(255), primary_key=True, index=True)
    token = Column(String(512), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
