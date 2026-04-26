"""
Application configuration loaded from environment variables.
All settings can be overridden via a .env file (loaded by python-dotenv in main.py).
"""
from __future__ import annotations

from pathlib import Path
import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


_ENV_FILE = str(Path(__file__).resolve().parent / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_title: str = "Mxsense Camera Service"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # ── Database (PostgreSQL / RDS) ───────────────────────────────────────────
    db_host: str = "mxsense-db.cfwsawyco4p4.ap-south-1.rds.amazonaws.com"
    db_port: int = 5432
    db_name: str = "mxsense_db"
    db_user: str = "mxsense_admin"
    db_password: str = "mxsense123"
    db_sslmode: str = "require"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # ── AWS ───────────────────────────────────────────────────────────────────
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    s3_bucket: str = "mxsense-images"
    s3_presigned_url_expiry: int = 3600  # seconds

    # ── ESP32 ─────────────────────────────────────────────────────────────────
    esp32_capture_timeout: int = 10       # seconds
    esp32_capture_path: str = "/capture"  # path on the device HTTP server

    # ── Scheduler (optional background capture) ───────────────────────────────
    scheduler_enabled: bool = False
    scheduler_interval_seconds: int = 30

    # ── DB behavior ─────────────────────────────────────────────────────────
    # In production you typically use migrations; this toggle avoids failing
    # FastAPI startup if the DB is temporarily unreachable.
    db_create_tables_on_startup: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
