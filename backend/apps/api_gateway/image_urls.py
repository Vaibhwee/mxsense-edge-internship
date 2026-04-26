"""
Resolve stored image paths to browser-loadable absolute URLs.

- Already-absolute http(s) URLs (e.g. S3 pre-signed) are returned unchanged.
- s3://bucket/key → optional pre-signed GET URL (boto3).
- Site-relative paths (including mistaken Next.js routes like /dashboard/modules/...) →
  Django MEDIA URL + request host (e.g. http://127.0.0.1:8000/media/...).
"""

from __future__ import annotations

import logging
import os
from urllib.parse import urljoin

from django.conf import settings

logger = logging.getLogger(__name__)


def _presign_s3_uri(s3_uri: str) -> str | None:
    """Return a pre-signed HTTPS URL for s3://bucket/key, or None."""
    low = s3_uri.strip().lower()
    if not low.startswith("s3://"):
        return None
    rest = s3_uri.strip()[5:]
    if "/" not in rest:
        return None
    bucket, _, key = rest.partition("/")
    bucket, key = bucket.strip(), key.lstrip("/")
    if not bucket or not key:
        return None
    try:
        import boto3  # type: ignore[import-not-found]
        from botocore.config import Config  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("boto3 not installed; cannot presign %s", s3_uri)
        return None

    region = getattr(settings, "AWS_S3_REGION_NAME", None) or os.getenv(
        "AWS_DEFAULT_REGION", "us-east-1"
    )
    expiry = int(
        getattr(settings, "AWS_PRESIGNED_URL_EXPIRY_SECONDS", 3600)
        or os.getenv("AWS_PRESIGNED_URL_EXPIRY_SECONDS", "3600")
    )
    client = boto3.client(
        "s3",
        region_name=region,
        config=Config(signature_version="s3v4"),
    )
    try:
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expiry,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("S3 presign failed for %s: %s", s3_uri, exc)
        return None


def _presign_s3_object_key(key: str) -> str | None:
    bucket = getattr(settings, "AWS_S3_IMAGE_BUCKET", None) or os.getenv(
        "AWS_S3_IMAGE_BUCKET", ""
    )
    if not bucket.strip():
        return None
    return _presign_s3_uri(f"s3://{bucket.strip()}/{key.lstrip('/')}")


def resolve_image_url_for_client(request, raw: str | None) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None

    low = s.lower()
    if low.startswith("http://") or low.startswith("https://"):
        return s

    if low.startswith("s3://"):
        signed = _presign_s3_uri(s)
        return signed or s

    use_key_presign = getattr(settings, "USE_S3_IMAGE_KEY_PRESIGN", False)
    if use_key_presign and not s.startswith("/") and "://" not in s:
        signed = _presign_s3_object_key(s)
        if signed:
            return signed

    media_url = getattr(settings, "MEDIA_URL", "/media/")
    if not media_url.startswith("/"):
        media_url = "/" + media_url
    if not media_url.endswith("/"):
        media_url = media_url + "/"

    # Wrong frontend-relative paths (served from localhost:3000) → under MEDIA.
    dash = "/dashboard/modules/"
    if s.startswith(dash):
        rel = s[len(dash) :].lstrip("/")
    elif low.startswith("dashboard/modules/"):
        rel = s.split("dashboard/modules/", 1)[-1].lstrip("/")
    elif s.startswith("/media/"):
        rel = s[len("/media/") :].lstrip("/")
    else:
        rel = s.lstrip("/")
        if rel.lower().startswith("media/"):
            rel = rel[6:].lstrip("/")

    if not rel:
        return None

    combined = urljoin(media_url, rel.replace("\\", "/"))
    if not combined.startswith("/"):
        combined = "/" + combined
    return request.build_absolute_uri(combined)


def normalize_latest_image_payload(request, payload: dict) -> dict:
    """Ensure image_url / url are absolute when a raw path was stored."""
    if not isinstance(payload, dict):
        return payload
    out = dict(payload)
    raw = out.get("image_url") or out.get("url")
    if raw is None or raw == "":
        return out
    resolved = resolve_image_url_for_client(request, str(raw))
    if resolved:
        out["image_url"] = resolved
        out["url"] = resolved
    return out
