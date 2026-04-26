"""
Mxsense Camera Service – FastAPI application entry point.

Start with:
    uvicorn camera_service.main:app --host 0.0.0.0 --port 8001 --reload

Or using the helper script:
    python -m camera_service.main
"""
from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from camera_service.config import get_settings
from camera_service.database import create_tables
from camera_service.routers.camera import router as camera_router
from camera_service.scheduler import start_scheduler, stop_scheduler

settings = get_settings()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up %s v%s …", settings.app_title, settings.app_version)

    if settings.db_create_tables_on_startup:
        await create_tables()
    start_scheduler()

    yield  # ← application serves requests here

    stop_scheduler()
    logger.info("Shutdown complete.")


# ── Application ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=(
        "Captures JPEG images from ESP32-CAM devices, stores them in AWS S3, "
        "persists metadata in PostgreSQL (RDS), and exposes APIs for the frontend."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(camera_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Service liveness probe")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "service": settings.app_title})


# ── Dev runner ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "camera_service.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
