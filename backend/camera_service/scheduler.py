"""
Optional background scheduler – periodically captures images from all
registered devices.

Enabled when SCHEDULER_ENABLED=true in the environment.
Uses APScheduler with an async job backend so it runs inside the same
event loop as FastAPI without blocking.
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from camera_service.config import get_settings
from camera_service.database import get_db_context
from camera_service.models import DeviceIP, Image
from camera_service.services.esp32 import (
    ESP32InvalidResponseError,
    ESP32NotReachableError,
    fetch_image,
)
from camera_service.services.s3 import S3UploadError, upload_image

logger = logging.getLogger(__name__)
settings = get_settings()

_scheduler: AsyncIOScheduler | None = None
_JOB_ID = "capture_all_devices"


def _ensure_scheduler_started() -> AsyncIOScheduler:
    global _scheduler  # noqa: PLW0603

    if _scheduler is not None and _scheduler.running:
        return _scheduler

    _scheduler = AsyncIOScheduler()
    _scheduler.start()
    return _scheduler


async def _capture_all_devices() -> None:
    """
    Iterate over all registered devices and capture + store an image for each.
    Failed devices are logged but do not interrupt other captures.
    """
    async with get_db_context() as db:
        result = await db.execute(select(DeviceIP))
        devices = result.scalars().all()

    if not devices:
        logger.debug("Scheduler: no devices registered, skipping cycle.")
        return

    logger.info("Scheduler: starting capture cycle for %d device(s).", len(devices))

    for device in devices:
        try:
            captured = await fetch_image(device.ip_address)
            s3_key = await upload_image(captured.data, device.device_id)

            async with get_db_context() as db:
                db.add(
                    Image(
                        device_id=device.device_id,
                        image_key=s3_key,
                        file_size_bytes=captured.size_bytes,
                    )
                )

            logger.info(
                "Scheduler: captured image for device %s → %s (%d bytes)",
                device.device_id,
                s3_key,
                captured.size_bytes,
            )
        except ESP32NotReachableError as exc:
            logger.warning(
                "Scheduler: device %s not reachable – %s", device.device_id, exc
            )
        except ESP32InvalidResponseError as exc:
            logger.warning(
                "Scheduler: invalid response from device %s – %s",
                device.device_id,
                exc,
            )
        except S3UploadError as exc:
            logger.error(
                "Scheduler: S3 upload failed for device %s – %s",
                device.device_id,
                exc,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Scheduler: unexpected error for device %s – %s",
                device.device_id,
                exc,
            )


def start_scheduler() -> None:
    global _scheduler  # noqa: PLW0603

    if not settings.scheduler_enabled:
        logger.info("Background capture scheduler is DISABLED (SCHEDULER_ENABLED=false).")
        return

    scheduler = _ensure_scheduler_started()
    scheduler.add_job(
        _capture_all_devices,
        trigger=IntervalTrigger(seconds=settings.scheduler_interval_seconds),
        id=_JOB_ID,
        name="Periodic ESP32 Capture",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    logger.info(
        "Background capture scheduler STARTED (interval=%ds).",
        settings.scheduler_interval_seconds,
    )


def stop_scheduler() -> None:
    global _scheduler  # noqa: PLW0603
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Background capture scheduler stopped.")
    _scheduler = None


def configure_scheduler(*, enabled: bool, interval_seconds: int) -> dict:
    """
    Configure the periodic capture scheduler at runtime.

    This is used by the web UI to set the fixed capture interval.
    """
    global _scheduler  # noqa: PLW0603

    interval_seconds = int(interval_seconds)
    if interval_seconds < 1:
        interval_seconds = 1

    if not enabled:
        stop_scheduler()
        return {"enabled": False, "interval_seconds": interval_seconds, "job_running": False}

    scheduler = _ensure_scheduler_started()

    # Add or replace the periodic job.
    scheduler.add_job(
        _capture_all_devices,
        trigger=IntervalTrigger(seconds=interval_seconds),
        id=_JOB_ID,
        name="Periodic ESP32 Capture",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    logger.info(
        "Background capture scheduler CONFIGURED (enabled=%s, interval=%ds).",
        enabled,
        interval_seconds,
    )
    return {
        "enabled": True,
        "interval_seconds": interval_seconds,
        "job_running": True,
    }
