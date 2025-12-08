# server/app/models/pill.py

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from ..schemas.database import Base  # 너가 기존에 쓰는 Base 그대로 맞춰서 import

class PillResult(Base):
    __tablename__ = "pill_results"

    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, index=True, nullable=False)

    # 업로드된 이미지 경로 (서버 내부 경로)
    image_path = Column(String, nullable=False)

    # LLM이 뽑아준 정보들
    pill_name = Column(String, nullable=True)        # 알약 이름 추정
    appearance = Column(Text, nullable=True)         # 모양/색/각인 요약
    main_usage = Column(Text, nullable=True)         # 주 사용 용도
    warning = Column(Text, nullable=True)            # 주의사항/경고
    extra_advice = Column(Text, nullable=True)       # 추가 조언

    # 원본 LLM JSON 전체를 문자열로 저장
    info_json = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

