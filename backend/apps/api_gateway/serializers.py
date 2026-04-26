from rest_framework import serializers

from .models import ApiEndpoint, ApiRequestLog, FrontendClient


class FrontendClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontendClient
        fields = "__all__"


class ApiEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiEndpoint
        fields = "__all__"


class ApiRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiRequestLog
        fields = "__all__"


class PlatformOverviewSerializer(serializers.Serializer):
    total_sites = serializers.IntegerField()
    total_devices = serializers.IntegerField()
    active_devices = serializers.IntegerField()
    active_protocol_adapters = serializers.IntegerField()
    active_sessions = serializers.IntegerField()
    queued_inference_jobs = serializers.IntegerField()
    open_alerts = serializers.IntegerField()
    pending_sync_jobs = serializers.IntegerField()
    pending_approvals = serializers.IntegerField()
    unhealthy_services = serializers.IntegerField()
