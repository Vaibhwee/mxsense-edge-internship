import uuid

from django.conf import settings
from django.db import models


class DataValidationRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_kind = models.CharField(max_length=32, default="sensor")
    sensor_type = models.CharField(max_length=64)
    schema_version = models.CharField(max_length=32, default="1.0")
    required_fields = models.JSONField(default=list, blank=True)
    transform_hints = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sensor_type", "-updated_at"]
        indexes = [
            models.Index(fields=["sensor_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.sensor_type} v{self.schema_version}"


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="sensors",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    sensor_code = models.CharField(max_length=64, unique=True)
    sensor_type = models.CharField(max_length=64)
    sensor_model = models.CharField(max_length=128, blank=True)
    unit = models.CharField(max_length=32, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sensor_code"]
        indexes = [
            models.Index(fields=["sensor_type"]),
            models.Index(fields=["sensor_code"]),
        ]

    def __str__(self):
        return self.sensor_code


class CalibrationProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_name = models.CharField(max_length=128, unique=True)
    sensor_type = models.CharField(max_length=64)
    parameters_json = models.JSONField(default=dict, blank=True)
    effective_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["profile_name"]
        indexes = [
            models.Index(fields=["sensor_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.profile_name


class Batch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_code = models.CharField(max_length=64, unique=True)
    product_name = models.CharField(max_length=128)
    supplier_name = models.CharField(max_length=128, blank=True)
    production_date = models.DateField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["batch_code"]),
            models.Index(fields=["product_name"]),
        ]

    def __str__(self):
        return self.batch_code


class Sample(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample_code = models.CharField(max_length=64, unique=True)
    batch = models.ForeignKey(
        Batch,
        related_name="samples",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    site = models.ForeignKey(
        "device_manager.Site",
        related_name="samples",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="samples",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="samples",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    collected_at = models.DateTimeField()
    sample_metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-collected_at"]
        indexes = [
            models.Index(fields=["sample_code"]),
            models.Index(fields=["collected_at"]),
        ]

    def __str__(self):
        return self.sample_code


class CollectionSession(models.Model):
    class SessionStatus(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_code = models.CharField(max_length=64, unique=True)
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="collection_sessions",
        on_delete=models.CASCADE,
    )
    batch = models.ForeignKey(
        Batch,
        related_name="sessions",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    sample = models.ForeignKey(
        Sample,
        related_name="sessions",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=16,
        choices=SessionStatus.choices,
        default=SessionStatus.SCHEDULED,
    )
    sampling_strategy = models.JSONField(default=dict, blank=True)
    context = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["session_code"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.session_code


class SensorReading(models.Model):
    class ValidationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        VALID = "valid", "Valid"
        INVALID = "invalid", "Invalid"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="sensor_readings",
        on_delete=models.CASCADE,
    )
    sample = models.ForeignKey(
        Sample,
        related_name="sensor_readings",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    session = models.ForeignKey(
        CollectionSession,
        related_name="sensor_readings",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    sensor = models.ForeignKey(
        Sensor,
        related_name="readings",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    sensor_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    quality_flags = models.JSONField(default=dict, blank=True)
    source_timestamp = models.DateTimeField(blank=True, null=True)
    ingest_source = models.CharField(max_length=32, default="api")
    topic = models.CharField(max_length=255, blank=True)
    sequence_number = models.PositiveIntegerField(blank=True, null=True)
    validation_status = models.CharField(
        max_length=16,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDING,
    )
    validation_errors = models.JSONField(default=list, blank=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sensor_type"]),
            models.Index(fields=["validation_status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.device.external_id} - {self.sensor_type}"


class ImageCapture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey(
        Sample,
        related_name="images",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    session = models.ForeignKey(
        CollectionSession,
        related_name="images",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="images",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    camera_id = models.CharField(max_length=64)
    file_uri = models.TextField()
    captured_at = models.DateTimeField()
    image_metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-captured_at"]
        indexes = [
            models.Index(fields=["camera_id"]),
            models.Index(fields=["captured_at"]),
        ]

    def __str__(self):
        return f"{self.camera_id} - {self.captured_at}"
