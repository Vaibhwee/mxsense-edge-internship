import uuid

from django.conf import settings
from django.db import models


class DecisionRule(models.Model):
    class RuleType(models.TextChoices):
        THRESHOLD = "threshold", "Threshold"
        ANOMALY = "anomaly", "Anomaly"
        BUSINESS = "business", "Business"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    rule_type = models.CharField(max_length=16, choices=RuleType.choices)
    priority = models.PositiveIntegerField(default=1)
    conditions_json = models.JSONField(default=dict, blank=True)
    actions_json = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "name"]
        indexes = [
            models.Index(fields=["rule_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class QualityScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey(
        "data_ingestion.Sample",
        related_name="quality_scores",
        on_delete=models.CASCADE,
    )
    inference_result = models.ForeignKey(
        "ai_orchestration.InferenceResult",
        related_name="quality_scores",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    freshness_score = models.DecimalField(max_digits=6, decimal_places=3)
    quality_index = models.DecimalField(max_digits=6, decimal_places=3)
    risk_band = models.CharField(max_length=32)
    decision = models.CharField(max_length=32)
    recommendation = models.TextField(blank=True)
    score_context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["risk_band"]),
            models.Index(fields=["decision"]),
        ]

    def __str__(self):
        return f"{self.sample.sample_code} - {self.decision}"


class NotificationRoute(models.Model):
    class Channel(models.TextChoices):
        UI = "ui", "UI"
        WEBHOOK = "webhook", "Webhook"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    channel = models.CharField(max_length=16, choices=Channel.choices)
    destination = models.CharField(max_length=255)
    severity_threshold = models.CharField(max_length=16, default="medium")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Alert(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class AlertStatus(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_service = models.CharField(max_length=128)
    severity = models.CharField(max_length=16, choices=Severity.choices)
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="alerts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    sample = models.ForeignKey(
        "data_ingestion.Sample",
        related_name="alerts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    message = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=AlertStatus.choices,
        default=AlertStatus.OPEN,
    )
    route = models.ForeignKey(
        NotificationRoute,
        related_name="alerts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    context = models.JSONField(default=dict, blank=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="acknowledged_alerts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["severity"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.message[:60]


class DecisionReview(models.Model):
    class ReviewAction(models.TextChoices):
        ACCEPT = "accept", "Accept"
        HOLD = "hold", "Hold"
        REJECT = "reject", "Reject"
        OVERRIDE = "override", "Override"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sample = models.ForeignKey(
        "data_ingestion.Sample",
        related_name="decision_reviews",
        on_delete=models.CASCADE,
    )
    quality_score = models.ForeignKey(
        QualityScore,
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="decision_reviews",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    action = models.CharField(max_length=16, choices=ReviewAction.choices)
    notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reviewed_at"]

    def __str__(self):
        return f"{self.sample.sample_code} - {self.action}"
