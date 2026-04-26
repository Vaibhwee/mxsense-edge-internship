"""
Camera API router.

Endpoints:
  POST /api/v1/devices/{device_id}/capture-and-store
  GET  /api/v1/devices/{device_id}/latest-image
  POST /api/v1/devices/{device_id}/ip              (register / update device IP)
  GET  /api/v1/devices/{device_id}/ip              (read device IP)
  GET  /api/v1/devices/{device_id}/images          (list captured images)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from camera_service.config import get_settings
from camera_service.database import get_db
from camera_service.models import DeviceIP, Image
from camera_service.schemas import (
    CaptureResponse,
    DeviceIPCreate,
    DeviceIPRead,
    DeviceIPUpdate,
    ImageRead,
    LatestImageResponse,
    SchedulerConfigRequest,
    SchedulerConfigResponse,
)
from camera_service.services.esp32 import (
    ESP32InvalidResponseError,
    ESP32NotReachableError,
    fetch_image,
)
from camera_service.services.s3 import (
    S3PresignError,
    S3UploadError,
    generate_presigned_url,
    upload_image,
)
from camera_service.scheduler import configure_scheduler

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api/v1/devices", tags=["Camera"])


# ── Scheduler (global periodic capture) ─────────────────────────────────────

@router.post(
    "/scheduler/config",
    response_model=SchedulerConfigResponse,
    summary="Configure periodic image capture interval",
    responses={400: {"description": "Invalid scheduler config"}},
)
async def set_scheduler_config(
    body: SchedulerConfigRequest,
) -> SchedulerConfigResponse:
    # APScheduler is synchronous to configure; just return the result.
    result = configure_scheduler(enabled=body.enabled, interval_seconds=body.interval_seconds)
    return SchedulerConfigResponse(**result)


# ── Helper ────────────────────────────────────────────────────────────────────

async def _get_device_ip_or_404(device_id: str, db: AsyncSession) -> DeviceIP:
    result = await db.execute(
        select(DeviceIP).where(DeviceIP.device_id == device_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found. Register it first via POST /ip.",
        )
    return record


# ── Device IP registration ────────────────────────────────────────────────────

@router.post(
    "/{device_id}/ip",
    response_model=DeviceIPRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register or update the IP address for a device",
)
async def register_device_ip(
    device_id: str = Path(..., min_length=1, max_length=128),
    body: DeviceIPCreate = ...,
    db: AsyncSession = Depends(get_db),
) -> DeviceIPRead:
    result = await db.execute(
        select(DeviceIP).where(DeviceIP.device_id == device_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.ip_address = body.ip_address
        if body.label is not None:
            existing.label = body.label
        existing.updated_at = datetime.now(timezone.utc)
        await db.flush()
        logger.info("Updated IP for device %s → %s", device_id, body.ip_address)
        return DeviceIPRead.model_validate(existing)

    record = DeviceIP(
        device_id=device_id,
        ip_address=body.ip_address,
        label=body.label,
    )
    db.add(record)
    await db.flush()
    logger.info("Registered device %s → %s", device_id, body.ip_address)
    return DeviceIPRead.model_validate(record)


@router.get(
    "/{device_id}/ip",
    response_model=DeviceIPRead,
    summary="Get registered IP address for a device",
)
async def get_device_ip(
    device_id: str = Path(...),
    db: AsyncSession = Depends(get_db),
) -> DeviceIPRead:
    record = await _get_device_ip_or_404(device_id, db)
    return DeviceIPRead.model_validate(record)


@router.delete(
    "/{device_id}/ip",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove registered IP mapping for a device",
    responses={404: {"description": "No mapping exists for this device"}},
)
async def remove_device_ip(
    device_id: str = Path(..., min_length=1, max_length=128),
    db: AsyncSession = Depends(get_db),
) -> Response:
    result = await db.execute(
        select(DeviceIP).where(DeviceIP.device_id == device_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device '{device_id}' not found.",
        )

    await db.execute(delete(DeviceIP).where(DeviceIP.device_id == device_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Capture & store ───────────────────────────────────────────────────────────

@router.post(
    "/{device_id}/capture-and-store",
    response_model=CaptureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Fetch image from ESP32, upload to S3, and save metadata to DB",
    responses={
        502: {"description": "ESP32 not reachable or returned invalid response"},
        503: {"description": "S3 upload or DB error"},
    },
)
async def capture_and_store(
    device_id: str = Path(..., min_length=1, max_length=128),
    db: AsyncSession = Depends(get_db),
) -> CaptureResponse:
    # 1. Resolve device → IP
    device = await _get_device_ip_or_404(device_id, db)

    # 2. Fetch image from ESP32
    try:
        captured = await fetch_image(device.ip_address)
    except ESP32NotReachableError as exc:
        logger.warning("ESP32 not reachable for device %s: %s", device_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ESP32 device not reachable: {exc}",
        ) from exc
    except ESP32InvalidResponseError as exc:
        logger.warning("ESP32 invalid response for device %s: %s", device_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid response from ESP32: {exc}",
        ) from exc

    # 3. Upload to S3
    try:
        s3_key = await upload_image(captured.data, device_id)
    except S3UploadError as exc:
        logger.error("S3 upload failed for device %s: %s", device_id, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to upload image to S3: {exc}",
        ) from exc

    # 4. Save metadata in DB
    try:
        image_record = Image(
            device_id=device_id,
            image_key=s3_key,
            file_size_bytes=captured.size_bytes,
        )
        db.add(image_record)
        await db.flush()
    except Exception as exc:
        logger.error("DB insert failed for device %s: %s", device_id, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error while saving image metadata: {exc}",
        ) from exc

    logger.info(
        "Captured and stored image for device %s: key=%s size=%d bytes",
        device_id, s3_key, captured.size_bytes,
    )
    return CaptureResponse(
        device_id=device_id,
        image_key=s3_key,
        image_id=image_record.id,
        file_size_bytes=captured.size_bytes,
        created_at=image_record.created_at,
    )


# ── Latest image ──────────────────────────────────────────────────────────────

@router.get(
    "/{device_id}/latest-image",
    response_model=LatestImageResponse,
    summary="Get a pre-signed URL for the most recent image from a device",
    responses={
        404: {"description": "No images found for device"},
        503: {"description": "Pre-signed URL generation failed"},
    },
)
async def latest_image(
    device_id: str = Path(..., min_length=1, max_length=128),
    db: AsyncSession = Depends(get_db),
) -> LatestImageResponse:
    # If the device is not currently mapped to an ESP32 IP, treat it as
    # "camera not assigned" even if old images exist in the images table.
    await _get_device_ip_or_404(device_id, db)

    result = await db.execute(
        select(Image)
        .where(Image.device_id == device_id)
        .order_by(Image.created_at.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No images found for device '{device_id}'.",
        )

    try:
        url = await generate_presigned_url(
            record.image_key, settings.s3_presigned_url_expiry
        )
    except S3PresignError as exc:
        logger.error("Presign failed for key %s: %s", record.image_key, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Could not generate pre-signed URL: {exc}",
        ) from exc

    return LatestImageResponse(
        device_id=device_id,
        image_id=record.id,
        image_key=record.image_key,
        image_url=url,
        expires_in_seconds=settings.s3_presigned_url_expiry,
        created_at=record.created_at,
    )


# ── List images ───────────────────────────────────────────────────────────────

@router.get(
    "/{device_id}/images",
    response_model=list[ImageRead],
    summary="List all captured image metadata for a device (newest first)",
)
async def list_images(
    device_id: str = Path(...),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> list[ImageRead]:
    # Enforce "camera assigned" semantics for listing too.
    await _get_device_ip_or_404(device_id, db)

    result = await db.execute(
        select(Image)
        .where(Image.device_id == device_id)
        .order_by(Image.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    records = result.scalars().all()
    return [ImageRead.model_validate(r) for r in records]
