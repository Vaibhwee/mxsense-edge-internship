"""
AWS S3 service – image upload and pre-signed URL generation.

All operations use boto3 in a thread-pool executor so they don't block
the async event loop.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from functools import lru_cache

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from camera_service.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class S3UploadError(Exception):
    """Raised when an image cannot be uploaded to S3."""


class S3PresignError(Exception):
    """Raised when a pre-signed URL cannot be generated."""


@lru_cache(maxsize=1)
def _get_s3_client():
    """Return a cached synchronous boto3 S3 client."""
    # Using an explicit regional endpoint avoids redirects that can invalidate
    # the pre-signed signature (leading to 403 on the client).
    endpoint_url = f"https://s3.{settings.aws_region}.amazonaws.com"
    kwargs: dict = {"region_name": settings.aws_region, "endpoint_url": endpoint_url}
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
    return boto3.client("s3", **kwargs)


def _build_s3_key(device_id: str, timestamp: datetime | None = None) -> str:
    """
    Construct the S3 object key in the format:
        {device_id}/{YYYY-MM-DDTHH-MM-SS-ffffff}.jpg
    """
    ts = timestamp or datetime.now(timezone.utc)
    filename = ts.strftime("%Y-%m-%dT%H-%M-%S-%f") + ".jpg"
    return f"{device_id}/{filename}"


def _upload_sync(image_data: bytes, s3_key: str) -> None:
    """Blocking upload – called via run_in_executor."""
    client = _get_s3_client()
    client.put_object(
        Bucket=settings.s3_bucket,
        Key=s3_key,
        Body=image_data,
        ContentType="image/jpeg",
    )


def _presign_sync(s3_key: str, expiry: int) -> str:
    """Blocking presign – called via run_in_executor."""
    client = _get_s3_client()
    url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": s3_key},
        ExpiresIn=expiry,
    )
    return url


async def upload_image(image_data: bytes, device_id: str) -> str:
    """
    Asynchronously upload *image_data* to S3 and return the S3 object key.

    Raises:
        S3UploadError on any boto3 / botocore failure.
    """
    s3_key = _build_s3_key(device_id)
    logger.info("Uploading image to s3://%s/%s", settings.s3_bucket, s3_key)

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, _upload_sync, image_data, s3_key)
    except (BotoCoreError, ClientError) as exc:
        raise S3UploadError(
            f"Failed to upload image to S3 (key={s3_key}): {exc}"
        ) from exc

    logger.info("Upload complete: s3://%s/%s", settings.s3_bucket, s3_key)
    return s3_key


async def generate_presigned_url(s3_key: str, expiry: int | None = None) -> str:
    """
    Asynchronously generate and return a pre-signed GET URL for *s3_key*.

    Raises:
        S3PresignError on any boto3 / botocore failure.
    """
    expiry = expiry or settings.s3_presigned_url_expiry
    logger.debug("Generating pre-signed URL for %s (expiry=%ds)", s3_key, expiry)

    loop = asyncio.get_event_loop()
    try:
        url = await loop.run_in_executor(None, _presign_sync, s3_key, expiry)
    except (BotoCoreError, ClientError) as exc:
        raise S3PresignError(
            f"Failed to generate pre-signed URL for {s3_key}: {exc}"
        ) from exc

    return url
