# app/main.py

import os
import uvicorn
from fastapi import FastAPI
from .routers import ingest, view  # ← view.py도 이제 포함하자
from fastapi.middleware.cors import CORSMiddleware
from .schemas.database import engine
from .models import health

app = FastAPI()

# CORS 설정 (웹 프론트와 통신 시 필수)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 중엔 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(ingest.router)
app.include_router(view.router)

# DB 테이블 생성 (초기 1회)
health.Base.metadata.create_all(bind=engine)

# 루트
@app.get("/")
def root():
    return {"msg": "Health API Server running!"}

# 서버 실행
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
