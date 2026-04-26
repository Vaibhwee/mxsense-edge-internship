from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ApiEndpointViewSet,
    ApiRequestLogViewSet,
    DevicesDataView,
    fetch_table_data,
    FrontendClientViewSet,
    LatestImageDataView,
    LocationsDataView,
    PlatformBlueprintView,
    PlatformOverviewView,
    SectionTelemetryDataView,
    TelemetryDataView,
)

router = DefaultRouter()
router.register("frontend-clients", FrontendClientViewSet, basename="frontend-client")
router.register("api-endpoints", ApiEndpointViewSet, basename="api-endpoint")
router.register("request-logs", ApiRequestLogViewSet, basename="api-request-log")

urlpatterns = [
    # Platform APIs
    path("overview/", PlatformOverviewView.as_view(), name="platform-overview"),
    path("blueprint/", PlatformBlueprintView.as_view(), name="platform-blueprint"),

    # Other APIs
    path("devices/", DevicesDataView.as_view(), name="devices-data"),
    path("latest-image/", LatestImageDataView.as_view(), name="latest-image-data"),
    path("data/", TelemetryDataView.as_view(), name="telemetry-data"),
    path("data/section/", SectionTelemetryDataView.as_view(), name="section-telemetry-data"),
    path("locations/", LocationsDataView.as_view(), name="locations-data"),

    # Keep this broad dynamic route last so it does not shadow specific API paths
    # like /devices/, /data/, /latest-image/, etc.
    path("<str:table_name>/", fetch_table_data, name="fetch-table-data"),
]

urlpatterns += router.urls