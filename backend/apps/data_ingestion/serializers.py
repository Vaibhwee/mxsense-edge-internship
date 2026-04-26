from django.utils import timezone
from rest_framework import serializers

from apps.device_manager.models import Device

from .models import (
    Batch,
    CalibrationProfile,
    CollectionSession,
    DataValidationRule,
    ImageCapture,
    Sample,
    Sensor,
    SensorReading,
)


class DataValidationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataValidationRule
        fields = "__all__"


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = "__all__"


class CalibrationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationProfile
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = "__all__"


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = "__all__"


class CollectionSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionSession
        fields = "__all__"


class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = "__all__"

    def create(self, validated_data):
        payload = validated_data.get("payload", {})
        sensor_type = validated_data["sensor_type"]
        active_rules = DataValidationRule.objects.filter(
            sensor_type=sensor_type,
            is_active=True,
        )

        errors = []
        for rule in active_rules:
            for field_name in rule.required_fields:
                if field_name not in payload:
                    errors.append(
                        f"Missing required field '{field_name}' for {sensor_type}."
                    )

        validated_data["validation_status"] = (
            SensorReading.ValidationStatus.INVALID
            if errors
            else SensorReading.ValidationStatus.VALID
        )
        validated_data["validation_errors"] = errors
        validated_data["processed_at"] = timezone.now()

        reading = super().create(validated_data)

        device = reading.device
        if device.status != Device.DeviceStatus.RETIRED:
            device.status = Device.DeviceStatus.ACTIVE
        device.last_seen_at = timezone.now()
        device.last_heartbeat_at = timezone.now()
        device.save()

        return reading


class ImageCaptureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCapture
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        raw = data.get("file_uri")
        if request and raw:
            from apps.api_gateway.image_urls import resolve_image_url_for_client

            absolute = resolve_image_url_for_client(request, str(raw))
            if absolute:
                data["file_uri"] = absolute
                data["image_url"] = absolute
        return data
