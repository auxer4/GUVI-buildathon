from fastapi import FastAPI
from app.api.detect import router as detect_router

app = FastAPI(
    title="Scam Detection Service",
    version="1.0.0"
)

app.include_router(detect_router)
