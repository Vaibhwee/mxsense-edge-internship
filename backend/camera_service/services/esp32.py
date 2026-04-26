"""
ESP32 camera capture service.

Fetches a JPEG image from an ESP32-CAM device over HTTP.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from camera_service.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ESP32NotReachableError(Exception):
    """Raised when the ESP32 device cannot be contacted."""


class ESP32InvalidResponseError(Exception):
    """Raised when the ESP32 returns an unexpected status or content type."""


@dataclass(frozen=True)
class CapturedImage:
    data: bytes
    content_type: str
    size_bytes: int


async def fetch_image(ip_address: str) -> CapturedImage:
    """
    Perform an async HTTP GET to http://<ip_address>/capture and return
    the raw JPEG bytes.

    Raises:
        ESP32NotReachableError  – on network / timeout errors.
        ESP32InvalidResponseError – on non-200 status or wrong content-type.
    """
    url = f"http://{ip_address}{settings.esp32_capture_path}"
    logger.info("Capturing image from ESP32 at %s", url)

    try:
        async with httpx.AsyncClient(timeout=settings.esp32_capture_timeout) as client:
            response = await client.get(url)
    except httpx.TimeoutException as exc:
        raise ESP32NotReachableError(
            f"Timed out connecting to ESP32 at {ip_address} "
            f"(timeout={settings.esp32_capture_timeout}s)"
        ) from exc
    except httpx.ConnectError as exc:
        raise ESP32NotReachableError(
            f"Could not connect to ESP32 at {ip_address}: {exc}"
        ) from exc
    except httpx.RequestError as exc:
        raise ESP32NotReachableError(
            f"Network error while reaching ESP32 at {ip_address}: {exc}"
        ) from exc

    if response.status_code != 200:
        raise ESP32InvalidResponseError(
            f"ESP32 returned HTTP {response.status_code} (expected 200). "
            f"Body: {response.text[:200]}"
        )

    content_type = response.headers.get("content-type", "")
    if "image/jpeg" not in content_type:
        raise ESP32InvalidResponseError(
            f"ESP32 returned unexpected content-type '{content_type}' "
            f"(expected image/jpeg)."
        )

    image_bytes = response.content
    logger.info(
        "Successfully captured %d bytes from %s", len(image_bytes), ip_address
    )
    return CapturedImage(
        data=image_bytes,
        content_type="image/jpeg",
        size_bytes=len(image_bytes),
    )
