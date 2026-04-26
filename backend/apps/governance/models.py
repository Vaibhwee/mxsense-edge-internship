import uuid

from django.conf import settings
from django.db import models


class PlatformRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_name = models.CharField(max_length=128, unique=True)
    permissions_json = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["role_name"]

    def __str__(self):
        return self.role_name


class AccessPolicy(models.Model):
    class PolicyType(models.TextChoices):
        ACCESS = "access", "Access"
        API = "api", "API"
        RETENTION = "retention", "Retention"
        ALERT = "alert", "Alert"
        DEVICE = "device", "Device"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    policy_type = models.CharField(max_length=16, choices=PolicyType.choices)
    version = models.CharField(max_length=32, default="1.0")
    rules_json = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ApprovalRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request_type = models.CharField(max_length=64)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="approval_requests",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    target_type = models.CharField(max_length=64)
    target_id = models.CharField(max_length=64)
    summary = models.TextField(blank=True)
    status = models.CharField(
        max_length=16,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["request_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.request_type} - {self.status}"


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="audit_logs",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    actor_type = models.CharField(max_length=64)
    action = models.CharField(max_length=128)
    target_type = models.CharField(max_length=64)
    target_id = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["target_type"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.target_type}"


class SecretCredential(models.Model):
    class SecretType(models.TextChoices):
        API_KEY = "api_key", "API Key"
        CERTIFICATE = "certificate", "Certificate"
        TOKEN = "token", "Token"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    secret_type = models.CharField(max_length=16, choices=SecretType.choices)
    reference = models.CharField(max_length=255)
    status = models.CharField(max_length=32, default="active")
    rotation_due_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
