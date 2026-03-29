"""FastAPI 애플리케이션 진입점."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import sources, research, outline, ppt

app = FastAPI(
    title="Deep Research PPT Generator",
    description="소스 기반 딥 리서치 및 PPT 자동 생성 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router, prefix="/api")
app.include_router(research.router, prefix="/api")
app.include_router(outline.router, prefix="/api")
app.include_router(ppt.router, prefix="/api")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "version": "0.1.0"}
