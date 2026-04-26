import uuid

from django.db import models


class StorageArtifact(models.Model):
    class ArtifactType(models.TextChoices):
        RAW = "raw", "Raw"
        PROCESSED = "processed", "Processed"
        RESULT = "result", "Result"
        EVIDENCE = "evidence", "Evidence"
        MODEL = "model", "Model"
        REPORT = "report", "Report"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artifact_type = models.CharField(max_length=16, choices=ArtifactType.choices)
    sample = models.ForeignKey(
        "data_ingestion.Sample",
        related_name="storage_artifacts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="storage_artifacts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    file_uri = models.TextField()
    storage_tier = models.CharField(max_length=32, default="local")
    size_bytes = models.BigIntegerField(default=0)
    checksum = models.CharField(max_length=128, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["artifact_type"]),
            models.Index(fields=["storage_tier"]),
        ]

    def __str__(self):
        return self.file_uri


class RetentionPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    target_type = models.CharField(max_length=32)
    retention_days = models.PositiveIntegerField()
    archive_after_days = models.PositiveIntegerField(blank=True, null=True)
    compression_enabled = models.BooleanField(default=False)
    rules_json = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class BackupJob(models.Model):
    class JobStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_name = models.CharField(max_length=128)
    scope = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=JobStatus.choices)
    output_uri = models.TextField(blank=True)
    notes = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.job_name


class SyncJob(models.Model):
    class SyncDirection(models.TextChoices):
        EDGE_TO_CLOUD = "edge_to_cloud", "Edge to Cloud"
        CLOUD_TO_EDGE = "cloud_to_edge", "Cloud to Edge"

    class JobStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sync_type = models.CharField(max_length=64)
    direction = models.CharField(max_length=16, choices=SyncDirection.choices)
    status = models.CharField(max_length=16, choices=JobStatus.choices)
    payload_ref = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sync_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.sync_type} - {self.status}"
