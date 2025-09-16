from fastapi import FastAPI
from .routers import ingest   # ← 상대 임포트로 변경 (.routers)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Health Backend (Demo)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 데모용 전체 허용 (배포 후에는 도메인 제한 권장)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
#python -m app.main