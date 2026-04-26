from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),

    # Existing services
    path("api/auth/", include("apps.authentication.urls")),
    path("api/api-gateway/", include("apps.api_gateway.urls")),
    path("api/device-manager/", include("apps.device_manager.urls")),
    path("api/data-ingestion/", include("apps.data_ingestion.urls")),
    path("api/mqtt-service/", include("apps.mqtt_service.urls")),
    path("api/ai-orchestration/", include("apps.ai_orchestration.urls")),
    path("api/quality-center/", include("apps.quality_center.urls")),
    path("api/monitoring/", include("apps.monitoring.urls")),
    path("api/storage-sync/", include("apps.storage_sync.urls")),
    path("api/governance/", include("apps.governance.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)