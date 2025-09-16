from fastapi import FastAPI
from .routers import ingest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Health Backend (Demo)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
