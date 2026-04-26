from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    AIHealthSummary,
    DeviceHealthSummary,
    IncidentCase,
    MetricSnapshot,
    PlatformLog,
    ServiceHealthCheck,
    TelemetryRecord,
)
from .serializers import (
    IncidentCaseSerializer,
    MetricSnapshotSerializer,
    PlatformLogSerializer,
    ServiceHealthCheckSerializer,
    TelemetryRecordSerializer,
)


class ServiceHealthCheckViewSet(viewsets.ModelViewSet):
    queryset = ServiceHealthCheck.objects.all()
    serializer_class = ServiceHealthCheckSerializer


class TelemetryRecordViewSet(viewsets.ModelViewSet):
    queryset = TelemetryRecord.objects.select_related("device").all()
    serializer_class = TelemetryRecordSerializer


class MetricSnapshotViewSet(viewsets.ModelViewSet):
    queryset = MetricSnapshot.objects.all()
    serializer_class = MetricSnapshotSerializer


class PlatformLogViewSet(viewsets.ModelViewSet):
    queryset = PlatformLog.objects.all()
    serializer_class = PlatformLogSerializer


class IncidentCaseViewSet(viewsets.ModelViewSet):
    queryset = IncidentCase.objects.select_related("device", "sample").all()
    serializer_class = IncidentCaseSerializer


class HealthOverviewView(APIView):
    def get(self, request):
        latest_by_service = {}

        for health_check in ServiceHealthCheck.objects.order_by(
            "service_name",
            "-checked_at",
        ):
            latest_by_service.setdefault(health_check.service_name, health_check)

        serializer = ServiceHealthCheckSerializer(
            latest_by_service.values(),
            many=True,
        )
        return Response(serializer.data)


class AIHealthView(APIView):
    def get(self, request, device_id):
        data = (
            AIHealthSummary.objects.filter(device_id=device_id)
            .prefetch_related("reasons")
            .order_by("-created_at")
            .first()
        )

        if not data:
            return Response(
                {"score": None, "status": None, "confidence": None, "reasons": []},
                status=200,
            )

        return Response(
            {
                "score": data.health_score,
                "status": data.health_status,
                "confidence": data.confidence_score,
                "reasons": [
                    {"code": r.reason_code, "msg": r.message, "severity": r.severity}
                    for r in data.reasons.all()
                ],
            }
        )


class DeviceHealthView(APIView):
    def get(self, request, device_id):
        data = (
            DeviceHealthSummary.objects.filter(device_id=device_id)
            .order_by("-created_at")
            .first()
        )

        if not data:
            return Response(
                {
                    "score": None,
                    "status": None,
                    "flow_ok": None,
                    "fan_ok": None,
                    "last_seen": None,
                },
                status=200,
            )

        return Response(
            {
                "score": data.health_score,
                "status": data.health_status,
                "flow_ok": data.flow_ok,
                "fan_ok": data.fan_ok,
                "last_seen": data.last_seen,
            }
        )
