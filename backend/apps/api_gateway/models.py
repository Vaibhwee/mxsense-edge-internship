import uuid

from django.db import models


class FrontendClient(models.Model):
    class ClientType(models.TextChoices):
        DASHBOARD = "dashboard", "Dashboard"
        MOBILE = "mobile", "Mobile"
        OPERATIONS = "operations", "Operations"

    class Environment(models.TextChoices):
        DEVELOPMENT = "development", "Development"
        STAGING = "staging", "Staging"
        PRODUCTION = "production", "Production"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    client_type = models.CharField(max_length=32, choices=ClientType.choices)
    environment = models.CharField(
        max_length=32,
        choices=Environment.choices,
        default=Environment.DEVELOPMENT,
    )
    allowed_origins = models.JSONField(default=list, blank=True)
    module_access = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    last_access_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["client_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class ApiEndpoint(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=16, default="GET")
    service_domain = models.CharField(max_length=64)
    auth_required = models.BooleanField(default=True)
    websocket_enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["service_domain", "path"]
        indexes = [
            models.Index(fields=["service_domain"]),
            models.Index(fields=["method"]),
        ]

    def __str__(self):
        return f"{self.method} {self.path}"


class ApiRequestLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(
        ApiEndpoint,
        related_name="request_logs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    client = models.ForeignKey(
        FrontendClient,
        related_name="request_logs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    request_path = models.CharField(max_length=255)
    method = models.CharField(max_length=16)
    status_code = models.PositiveIntegerField()
    latency_ms = models.PositiveIntegerField(default=0)
    response_size_bytes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status_code"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.method} {self.request_path}"
