import uuid

from django.db import models


class Site(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site_code = models.CharField(max_length=64, unique=True)
    site_name = models.CharField(max_length=128)
    location_name = models.CharField(max_length=128, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
    )
    timezone = models.CharField(max_length=64, default="UTC")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["site_name"]
        indexes = [
            models.Index(fields=["site_code"]),
            models.Index(fields=["site_name"]),
        ]

    def __str__(self):
        return self.site_name


class Device(models.Model):
    class DeviceStatus(models.TextChoices):
        REGISTERED = "registered", "Registered"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        OFFLINE = "offline", "Offline"
        PAUSED = "paused", "Paused"
        MAINTENANCE = "maintenance", "Maintenance"
        RETIRED = "retired", "Retired"

    class ProvisioningStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PROVISIONED = "provisioned", "Provisioned"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128)
    site = models.ForeignKey(
        Site,
        related_name="devices",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    device_type = models.CharField(max_length=64)
    location = models.CharField(max_length=128, blank=True)
    assigned_line = models.CharField(max_length=128, blank=True)
    connectivity_type = models.CharField(max_length=32, blank=True)
    status = models.CharField(
        max_length=16,
        choices=DeviceStatus.choices,
        default=DeviceStatus.REGISTERED,
    )
    provisioning_status = models.CharField(
        max_length=16,
        choices=ProvisioningStatus.choices,
        default=ProvisioningStatus.PENDING,
    )
    firmware_version = models.CharField(max_length=64, blank=True)
    configuration_version = models.CharField(max_length=64, blank=True)
    certificate_status = models.CharField(max_length=32, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    last_seen_at = models.DateTimeField(blank=True, null=True)
    last_heartbeat_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["external_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["device_type"]),
            models.Index(fields=["assigned_line"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.external_id})"


class DeviceChannel(models.Model):
    class ChannelStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        FAULTED = "faulted", "Faulted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        Device,
        related_name="channels",
        on_delete=models.CASCADE,
    )
    channel_code = models.CharField(max_length=64)
    channel_name = models.CharField(max_length=128)
    sensor_type = models.CharField(max_length=64, blank=True)
    status = models.CharField(
        max_length=16,
        choices=ChannelStatus.choices,
        default=ChannelStatus.ACTIVE,
    )
    configuration = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["device__name", "channel_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["device", "channel_code"],
                name="unique_device_channel_code",
            )
        ]

    def __str__(self):
        return f"{self.device.external_id}:{self.channel_code}"


class DeviceConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        Device,
        related_name="configurations",
        on_delete=models.CASCADE,
    )
    config_version = models.CharField(max_length=64)
    sampling_rate_hz = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    thresholds = models.JSONField(default=dict, blank=True)
    trigger_rules = models.JSONField(default=dict, blank=True)
    sensors_enabled = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=False)
    applied_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["device", "config_version"],
                name="unique_device_config_version",
            )
        ]

    def __str__(self):
        return f"{self.device.external_id} - {self.config_version}"


class FirmwareUpdateJob(models.Model):
    class JobStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        Device,
        related_name="firmware_jobs",
        on_delete=models.CASCADE,
    )
    target_version = models.CharField(max_length=64)
    status = models.CharField(
        max_length=16,
        choices=JobStatus.choices,
        default=JobStatus.PENDING,
    )
    scheduled_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    notes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["target_version"]),
        ]

    def __str__(self):
        return f"{self.device.external_id} -> {self.target_version}"


class DeviceLifecycleEvent(models.Model):
    class EventType(models.TextChoices):
        REGISTERED = "registered", "Registered"
        PROVISIONED = "provisioned", "Provisioned"
        HEARTBEAT = "heartbeat", "Heartbeat"
        MAINTENANCE = "maintenance", "Maintenance"
        DECOMMISSIONED = "decommissioned", "Decommissioned"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(
        Device,
        related_name="lifecycle_events",
        on_delete=models.CASCADE,
    )
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    status = models.CharField(max_length=16, choices=Device.DeviceStatus.choices)
    details = models.JSONField(default=dict, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["recorded_at"]),
        ]

    def __str__(self):
        return f"{self.device.external_id} - {self.event_type}"
