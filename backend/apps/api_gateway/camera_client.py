"""HTTP client for the camera microservice (device ↔ ESP32 assignment + captures)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def camera_service_base() -> str:
    return os.getenv("CAMERA_SERVICE_URL", "http://127.0.0.1:8011").rstrip("/")


def camera_service_get(path: str, timeout: float = 8.0) -> tuple[int | None, dict[str, Any]]:
    """GET a path on the camera service. Returns (http_status_or_none, parsed_json_body)."""
    url = f"{camera_service_base()}{path}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            body = json.loads(raw) if raw.strip() else {}
            return resp.status, body if isinstance(body, dict) else {"data": body}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8") if exc.fp else ""
        try:
            body = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            body = {"detail": raw or str(exc)}
        if not isinstance(body, dict):
            body = {"detail": str(body)}
        return exc.code, body
    except urllib.error.URLError as exc:
        reason = exc.reason
        refused = isinstance(reason, ConnectionRefusedError)
        if not refused and isinstance(reason, OSError):
            refused = reason.errno in (61, 111)  # macOS / Linux connection refused
        base = camera_service_base()
        if refused:
            detail = (
                "Camera service is not running or refused the connection. "
                f"Start it or point CAMERA_SERVICE_URL to the correct host (tried {base})."
            )
        else:
            detail = f"Could not reach camera service at {base}: {reason or exc}"
        return None, {"detail": detail}
    except Exception as exc:  # noqa: BLE001
        base = camera_service_base()
        return None, {
            "detail": (
                f"Camera service request failed ({base}): {exc}"
            ),
        }
