import uuid

from django.conf import settings
from django.db import models


class PreprocessingProfile(models.Model):
    class Modality(models.TextChoices):
        SIGNAL = "signal", "Signal"
        IMAGE = "image", "Image"
        FUSION = "fusion", "Fusion"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_name = models.CharField(max_length=128, unique=True)
    modality = models.CharField(max_length=16, choices=Modality.choices)
    target_domain = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["profile_name"]
        indexes = [
            models.Index(fields=["modality"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.profile_name


class ProcessedRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey(
        "data_ingestion.Sample",
        related_name="processed_records",
        on_delete=models.CASCADE,
    )
    session = models.ForeignKey(
        "data_ingestion.CollectionSession",
        related_name="processed_records",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    preprocessing_profile = models.ForeignKey(
        PreprocessingProfile,
        related_name="processed_records",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    processed_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Processed {self.sample.sample_code}"


class FeatureVector(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey(
        "data_ingestion.Sample",
        related_name="feature_vectors",
        on_delete=models.CASCADE,
    )
    processed_record = models.ForeignKey(
        ProcessedRecord,
        related_name="feature_vectors",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    feature_type = models.CharField(max_length=64)
    feature_json = models.JSONField(default=dict, blank=True)
    version = models.CharField(max_length=32)
    health_score = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["feature_type"]),
            models.Index(fields=["version"]),
        ]

    def __str__(self):
        return f"{self.sample.sample_code} - {self.feature_type}"


class ModelArtifact(models.Model):
    class ModelType(models.TextChoices):
        SENSING = "sensing", "Sensing"
        VISION = "vision", "Vision"
        FUSION = "fusion", "Fusion"

    class ModelStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        CANARY = "canary", "Canary"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_name = models.CharField(max_length=128)
    model_type = models.CharField(max_length=16, choices=ModelType.choices)
    version = models.CharField(max_length=32)
    runtime_type = models.CharField(max_length=64)
    status = models.CharField(
        max_length=16,
        choices=ModelStatus.choices,
        default=ModelStatus.INACTIVE,
    )
    artifact_uri = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["model_name", "-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["model_name", "version"],
                name="unique_model_name_version",
            )
        ]

    def __str__(self):
        return f"{self.model_name}:{self.version}"


class InferenceJob(models.Model):
    class JobStatus(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey(
        "data_ingestion.Sample",
        related_name="inference_jobs",
        on_delete=models.CASCADE,
    )
    feature_vector = models.ForeignKey(
        FeatureVector,
        related_name="inference_jobs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    model = models.ForeignKey(
        ModelArtifact,
        related_name="inference_jobs",
        on_delete=models.CASCADE,
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="inference_jobs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    job_type = models.CharField(max_length=64)
    status = models.CharField(
        max_length=16,
        choices=JobStatus.choices,
        default=JobStatus.QUEUED,
    )
    request_metadata = models.JSONField(default=dict, blank=True)
    queued_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-queued_at"]
        indexes = [
            models.Index(fields=["job_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.sample.sample_code} - {self.job_type}"


class InferenceResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(
        InferenceJob,
        related_name="results",
        on_delete=models.CASCADE,
    )
    result_type = models.CharField(max_length=64)
    label = models.CharField(max_length=128, blank=True)
    risk_band = models.CharField(max_length=32, blank=True)
    result_json = models.JSONField(default=dict, blank=True)
    confidence_score = models.DecimalField(max_digits=6, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["result_type"]),
        ]

    def __str__(self):
        return f"{self.job_id} - {self.result_type}"
