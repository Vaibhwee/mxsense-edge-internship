from rest_framework import serializers

from .models import (
    Device,
    DeviceChannel,
    DeviceConfiguration,
    DeviceLifecycleEvent,
    FirmwareUpdateJob,
    Site,
)


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"


class DeviceChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceChannel
        fields = "__all__"


class DeviceConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceConfiguration
        fields = "__all__"


class FirmwareUpdateJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirmwareUpdateJob
        fields = "__all__"


class DeviceLifecycleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLifecycleEvent
        fields = "__all__"


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"

