from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AIHealthView,
    DeviceHealthView,
    HealthOverviewView,
    IncidentCaseViewSet,
    MetricSnapshotViewSet,
    PlatformLogViewSet,
    ServiceHealthCheckViewSet,
    TelemetryRecordViewSet,
)


router = DefaultRouter()
router.register("health-checks", ServiceHealthCheckViewSet, basename="health-check")
router.register("telemetry-records", TelemetryRecordViewSet, basename="telemetry-record")
router.register("metrics", MetricSnapshotViewSet, basename="metric-snapshot")
router.register("logs", PlatformLogViewSet, basename="platform-log")
router.register("incidents", IncidentCaseViewSet, basename="incident-case")

urlpatterns = [
    path("overview/", HealthOverviewView.as_view(), name="health-overview"),
    path("ai-health/<uuid:device_id>/", AIHealthView.as_view(), name="ai-health"),
    path("device-health/<uuid:device_id>/", DeviceHealthView.as_view(), name="device-health"),
]
urlpatterns += router.urls
