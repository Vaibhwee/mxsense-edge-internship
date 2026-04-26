import uuid

from django.db import models


class ServiceHealthCheck(models.Model):
    class HealthStatus(models.TextChoices):
        HEALTHY = "healthy", "Healthy"
        DEGRADED = "degraded", "Degraded"
        UNHEALTHY = "unhealthy", "Unhealthy"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_name = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=HealthStatus.choices)
    details = models.JSONField(default=dict, blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-checked_at"]
        indexes = [
            models.Index(fields=["service_name"]),
            models.Index(fields=["status"]),
            models.Index(fields=["checked_at"]),
        ]

    def __str__(self):
        return f"{self.service_name} - {self.status}"


class TelemetryRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="telemetry_records",
        on_delete=models.CASCADE,
    )
    timestamp_utc = models.DateTimeField()
    cpu_temp_c = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
    )
    battery_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )
    health_state = models.CharField(max_length=32, blank=True)
    telemetry_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp_utc"]
        indexes = [
            models.Index(fields=["timestamp_utc"]),
            models.Index(fields=["health_state"]),
        ]

    def __str__(self):
        return f"{self.device.external_id} @ {self.timestamp_utc}"


class MetricSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.CharField(max_length=128)
    metric_name = models.CharField(max_length=128)
    metric_value = models.DecimalField(max_digits=12, decimal_places=3)
    unit = models.CharField(max_length=32, blank=True)
    tags = models.JSONField(default=dict, blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-captured_at"]
        indexes = [
            models.Index(fields=["component"]),
            models.Index(fields=["metric_name"]),
            models.Index(fields=["captured_at"]),
        ]

    def __str__(self):
        return f"{self.component} - {self.metric_name}"


class PlatformLog(models.Model):
    class Severity(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        ERROR = "error", "Error"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.CharField(max_length=128)
    severity = models.CharField(max_length=16, choices=Severity.choices)
    message = models.TextField()
    context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["component"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.component} - {self.severity}"


class IncidentCase(models.Model):
    class IncidentStatus(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    source_service = models.CharField(max_length=128)
    severity = models.CharField(max_length=16, choices=Severity.choices)
    status = models.CharField(
        max_length=16,
        choices=IncidentStatus.choices,
        default=IncidentStatus.OPEN,
    )
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="incident_cases",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    sample = models.ForeignKey(
        "data_ingestion.Sample",
        related_name="incident_cases",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    root_cause_hint = models.TextField(blank=True)
    impacted_services = models.JSONField(default=list, blank=True)
    details = models.JSONField(default=dict, blank=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-opened_at"]
        indexes = [
            models.Index(fields=["source_service"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.title


class AIHealthSummary(models.Model):
    class HealthStatus(models.TextChoices):
        HEALTHY = "HEALTHY", "Healthy"
        DEGRADED = "DEGRADED", "Degraded"
        UNRELIABLE = "UNRELIABLE", "Unreliable"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        "device_manager.Device",
        on_delete=models.CASCADE,
        related_name="ai_health_summaries",
    )

    run_id = models.UUIDField(null=True, blank=True)

    health_score = models.FloatField()
    health_status = models.CharField(max_length=20, choices=HealthStatus.choices)

    confidence_score = models.FloatField()

    gating_valid = models.BooleanField(default=True)
    signal_quality = models.FloatField(default=1.0)
    channel_consistency = models.FloatField(default=1.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["device", "created_at"]),
            models.Index(fields=["health_status"]),
        ]

    def __str__(self):
        return f"AIHealth({self.device.external_id}) {self.health_status} {self.health_score}"


class AIHealthExplanation(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ai_health = models.ForeignKey(
        AIHealthSummary,
        on_delete=models.CASCADE,
        related_name="reasons",
    )
    reason_code = models.CharField(max_length=100)
    message = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["reason_code"]),
            models.Index(fields=["severity"]),
        ]

    def __str__(self):
        return f"{self.reason_code} ({self.severity})"


class DeviceHealthSummary(models.Model):
    class HealthStatus(models.TextChoices):
        HEALTHY = "HEALTHY", "Healthy"
        WARNING = "WARNING", "Warning"
        CRITICAL = "CRITICAL", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        "device_manager.Device",
        on_delete=models.CASCADE,
        related_name="device_health_summaries",
    )

    health_score = models.FloatField()
    health_status = models.CharField(max_length=20, choices=HealthStatus.choices)

    sampling_integrity = models.FloatField(default=1.0)
    sensor_health = models.FloatField(default=1.0)
    env_stability = models.FloatField(default=1.0)
    connectivity = models.FloatField(default=1.0)
    maintenance = models.FloatField(default=1.0)

    flow_ok = models.BooleanField(default=True)
    fan_ok = models.BooleanField(default=True)
    clog_risk = models.BooleanField(default=False)

    last_seen = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["device", "created_at"]),
            models.Index(fields=["health_status"]),
        ]

    def __str__(self):
        return f"DeviceHealth({self.device.external_id}) {self.health_status} {self.health_score}"
