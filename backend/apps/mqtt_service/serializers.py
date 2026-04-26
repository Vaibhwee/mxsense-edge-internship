from django.utils import timezone
from rest_framework import serializers

from apps.device_manager.models import Device

from .models import MqttMessageLog, ProtocolAdapter, SchemaMapping, TopicSubscription


class ProtocolAdapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocolAdapter
        fields = "__all__"


class TopicSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicSubscription
        fields = "__all__"


class SchemaMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemaMapping
        fields = "__all__"


class MqttMessageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MqttMessageLog
        fields = "__all__"

    def create(self, validated_data):
        message = super().create(validated_data)

        if message.subscription:
            subscription = message.subscription
            subscription.last_message_at = message.received_at
            subscription.save()

        if message.device and message.device.status != Device.DeviceStatus.RETIRED:
            device = message.device
            device.status = Device.DeviceStatus.ACTIVE
            device.last_seen_at = timezone.now()
            device.last_heartbeat_at = timezone.now()
            device.save()

        return message
