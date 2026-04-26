import uuid

from django.db import models


class ProtocolAdapter(models.Model):
    class AdapterType(models.TextChoices):
        MQTT = "mqtt", "MQTT"
        RTSP = "rtsp", "RTSP"
        MODBUS = "modbus", "Modbus"
        SERIAL = "serial", "Serial"
        API = "api", "API"

    class AdapterStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        ERROR = "error", "Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128, unique=True)
    adapter_type = models.CharField(max_length=16, choices=AdapterType.choices)
    endpoint = models.CharField(max_length=255)
    status = models.CharField(
        max_length=16,
        choices=AdapterStatus.choices,
        default=AdapterStatus.ACTIVE,
    )
    config = models.JSONField(default=dict, blank=True)
    last_tested_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["adapter_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name


class TopicSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adapter = models.ForeignKey(
        ProtocolAdapter,
        related_name="topic_subscriptions",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=128, unique=True)
    topic_pattern = models.CharField(max_length=255, unique=True)
    qos = models.PositiveSmallIntegerField(default=0)
    parser_name = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)
    retain_enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    last_message_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["topic_pattern"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.topic_pattern})"


class SchemaMapping(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adapter = models.ForeignKey(
        ProtocolAdapter,
        related_name="schema_mappings",
        on_delete=models.CASCADE,
    )
    source_field = models.CharField(max_length=128)
    target_field = models.CharField(max_length=128)
    transform_rule = models.CharField(max_length=255, blank=True)
    is_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["adapter__name", "source_field"]
        constraints = [
            models.UniqueConstraint(
                fields=["adapter", "source_field", "target_field"],
                name="unique_schema_mapping",
            )
        ]

    def __str__(self):
        return f"{self.source_field} -> {self.target_field}"


class MqttMessageLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        TopicSubscription,
        related_name="messages",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    device = models.ForeignKey(
        "device_manager.Device",
        related_name="mqtt_messages",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    topic = models.CharField(max_length=255)
    payload = models.JSONField(default=dict)
    qos = models.PositiveSmallIntegerField(default=0)
    retain = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    processing_notes = models.JSONField(default=dict, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-received_at"]
        indexes = [
            models.Index(fields=["topic"]),
            models.Index(fields=["processed"]),
            models.Index(fields=["received_at"]),
        ]

    def __str__(self):
        return self.topic
