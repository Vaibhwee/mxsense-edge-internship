"""
SQLAlchemy ORM models.

Tables:
  device_ips  – maps device_id → ESP32 IP address
  images      – metadata for every image captured and stored in S3
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from camera_service.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DeviceIP(Base):
    """Registry that maps a logical device_id to its ESP32 IP address."""

    __tablename__ = "device_ips"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    device_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    label: Mapped[str] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<DeviceIP device_id={self.device_id} ip={self.ip_address}>"


class Image(Base):
    """Metadata record for each image captured from an ESP32 and stored in S3."""

    __tablename__ = "images"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    device_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    image_key: Mapped[str] = mapped_column(Text, nullable=False)   # S3 object key
    file_size_bytes: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, server_default=func.now(), index=True
    )

    __table_args__ = (
        Index("ix_images_device_created", "device_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Image device_id={self.device_id} key={self.image_key}>"
