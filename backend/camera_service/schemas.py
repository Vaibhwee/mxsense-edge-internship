"""
Pydantic v2 request / response schemas.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ── DeviceIP ──────────────────────────────────────────────────────────────────

class DeviceIPCreate(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=128)
    ip_address: str = Field(..., min_length=7, max_length=45)
    label: str | None = Field(None, max_length=128)


class DeviceIPRead(DeviceIPCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class DeviceIPUpdate(BaseModel):
    ip_address: str | None = Field(None, min_length=7, max_length=45)
    label: str | None = Field(None, max_length=128)


# ── Image ─────────────────────────────────────────────────────────────────────

class ImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str
    image_key: str
    file_size_bytes: int | None
    created_at: datetime


# ── API responses ─────────────────────────────────────────────────────────────

class CaptureResponse(BaseModel):
    """Returned after a successful capture-and-store operation."""
    device_id: str
    image_key: str
    image_id: str
    file_size_bytes: int | None
    created_at: datetime
    message: str = "Image captured and stored successfully."


class LatestImageResponse(BaseModel):
    """Returned by GET /latest-image."""
    device_id: str
    image_id: str
    image_key: str
    image_url: str          # pre-signed S3 URL
    expires_in_seconds: int
    created_at: datetime


class ErrorDetail(BaseModel):
    detail: str


# ── Scheduler config ─────────────────────────────────────────────────────────

class SchedulerConfigRequest(BaseModel):
    enabled: bool = Field(True, description="Enable or disable periodic capture.")
    interval_seconds: int = Field(
        30, ge=1, le=3600, description="Capture interval in seconds."
    )


class SchedulerConfigResponse(BaseModel):
    enabled: bool
    interval_seconds: int
    job_running: bool
