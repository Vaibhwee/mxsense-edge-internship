from rest_framework import serializers

from .models import IncidentCase, MetricSnapshot, PlatformLog, ServiceHealthCheck, TelemetryRecord


class ServiceHealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceHealthCheck
        fields = "__all__"


class TelemetryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryRecord
        fields = "__all__"


class MetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricSnapshot
        fields = "__all__"


class PlatformLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformLog
        fields = "__all__"


class IncidentCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentCase
        fields = "__all__"
