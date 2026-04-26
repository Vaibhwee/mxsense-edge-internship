from urllib.parse import quote

import logging
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_orchestration.models import InferenceJob
from apps.data_ingestion.models import CollectionSession
from apps.device_manager.models import Device, Site
from apps.governance.models import ApprovalRequest
from apps.monitoring.models import ServiceHealthCheck
from apps.mqtt_service.models import ProtocolAdapter
from apps.quality_center.models import Alert
from apps.storage_sync.models import SyncJob

from .blueprint import BACKEND_SERVICES, OPERATOR_WORKFLOWS, PRIMARY_MODULES, STACK_LAYERS
from .camera_client import camera_service_get
from .image_urls import normalize_latest_image_payload
from .db import (
    get_devices_data,
    get_latest_image_data,
    get_locations_data,
    get_section_timeseries,
    get_telemetry_data,
    resolve_device_identity,
)
from .models import ApiEndpoint, ApiRequestLog, FrontendClient
from .serializers import (
    ApiEndpointSerializer,
    ApiRequestLogSerializer,
    FrontendClientSerializer,
    PlatformOverviewSerializer,
)

logger = logging.getLogger(__name__)

ALLOWED_TABLES = [
    "tenant",
    "enterprise",
    "sites",
    "business_unit",
    "users",
    "roles",
    "user_role",
    "devices",
    "sensors",
    "device_sensors",
    "device_channels",
    "raw_sensor_data",
    "samples",
    "batches",
    "quality_scores",
    "images",
    "alerts",
    "audit_logs",
    "sync_jobs",
    "calibration_profiles",
    "telemetry_data",
    "processed_data",
    "feature_vectors",
    "models",
    "inference_jobs",
    "inference_results",
]


def _quote_ident(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _json_status(message: str, status_code: int, **extra):
    payload = {"status": "error" if status_code >= 400 else "success", "message": message}
    payload.update(extra)
    return JsonResponse(payload, status=status_code)


def _validate_api_key_for_table(api_key: str, requested_table: str):
    """
    Validate API key access against api_keys table.
    Returns: (True, None) on success, otherwise (False, "invalid_key"|"table_mismatch").
    """
    with connection.cursor() as cursor:
        api_key_preview = f"{api_key[:4]}..." if api_key else "<empty>"
        logger.debug(
            "Validating API key for table access (table=%s key=%s).",
            requested_table,
            api_key_preview,
        )
        cursor.execute(
            """
            SELECT 1
            FROM api_keys
            WHERE api_key = %s
              AND table_name = %s
              AND is_active = TRUE
            LIMIT 1;
            """,
            [api_key, requested_table],
        )
        if cursor.fetchone() is not None:
            logger.info(
                "API key authorized for table access (table=%s key=%s).",
                requested_table,
                api_key_preview,
            )
            return True, None

        cursor.execute(
            """
            SELECT 1
            FROM api_keys
            WHERE api_key = %s
              AND is_active = TRUE
            LIMIT 1;
            """,
            [api_key],
        )
        if cursor.fetchone() is not None:
            logger.warning(
                "API key table mismatch (table=%s key=%s).",
                requested_table,
                api_key_preview,
            )
            return False, "table_mismatch"
    logger.warning(
        "Invalid/inactive API key attempted table access (table=%s key=%s).",
        requested_table,
        api_key_preview,
    )
    return False, "invalid_key"


@require_GET
def fetch_table_data(request, table_name):
    api_key = request.headers.get("x-api-key")
    if not api_key:
        logger.warning(
            "Rejected table fetch due to missing API key (table=%s).",
            table_name,
        )
        return JsonResponse({"status": "error", "message": "Missing API key."}, status=403)

    table_name = (table_name or "").strip().lower()
    if table_name not in ALLOWED_TABLES:
        logger.warning("Rejected table fetch for non-allowlisted table (table=%s).", table_name)
        return JsonResponse({"status": "error", "message": "Invalid table."}, status=400)

    # Limit number of rows returned (default 100)
    limit = request.GET.get("limit", 100)
    try:
        limit = int(limit)
    except Exception:
        limit = 100

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT table_name FROM api_keys WHERE api_key = %s AND is_active = TRUE",
                [api_key],
            )
            allowed_for_key = {row[0].lower() for row in cursor.fetchall() if row and row[0]}

            if not allowed_for_key:
                return JsonResponse({"status": "error", "message": "Invalid API key."}, status=403)
            if table_name not in allowed_for_key:
                return JsonResponse(
                    {"status": "error", "message": "Table mismatch for API key."},
                    status=403,
                )

            query = f'SELECT * FROM public."{table_name}" LIMIT %s'
            cursor.execute(query, [limit])
            columns = [col[0] for col in (cursor.description or [])]
            rows = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in rows]
        # Remove sensitive fields before sending response
        for row in data:
            row.pop("password_hash", None)
        return JsonResponse({"status": "success", "data": data}, status=200, safe=False)
    except Exception as e:
        logger.exception("fetch_table_data failed (table=%s): %s", table_name, e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


class FrontendClientViewSet(viewsets.ModelViewSet):
    queryset = FrontendClient.objects.all()
    serializer_class = FrontendClientSerializer


class ApiEndpointViewSet(viewsets.ModelViewSet):
    queryset = ApiEndpoint.objects.all()
    serializer_class = ApiEndpointSerializer


class ApiRequestLogViewSet(viewsets.ModelViewSet):
    queryset = ApiRequestLog.objects.select_related("endpoint", "client").all()
    serializer_class = ApiRequestLogSerializer


class PlatformOverviewView(APIView):
    def get(self, request):
        payload = {
            "total_sites": Site.objects.count(),
            "total_devices": Device.objects.count(),
            "active_devices": Device.objects.filter(
                status=Device.DeviceStatus.ACTIVE
            ).count(),
            "active_protocol_adapters": ProtocolAdapter.objects.filter(
                status=ProtocolAdapter.AdapterStatus.ACTIVE
            ).count(),
            "active_sessions": CollectionSession.objects.filter(
                status=CollectionSession.SessionStatus.ACTIVE
            ).count(),
            "queued_inference_jobs": InferenceJob.objects.filter(
                status=InferenceJob.JobStatus.QUEUED
            ).count(),
            "open_alerts": Alert.objects.filter(
                status=Alert.AlertStatus.OPEN
            ).count(),
            "pending_sync_jobs": SyncJob.objects.filter(
                status=SyncJob.JobStatus.PENDING
            ).count(),
            "pending_approvals": ApprovalRequest.objects.filter(
                status=ApprovalRequest.RequestStatus.PENDING
            ).count(),
            "unhealthy_services": ServiceHealthCheck.objects.filter(
                status__in=[
                    ServiceHealthCheck.HealthStatus.DEGRADED,
                    ServiceHealthCheck.HealthStatus.UNHEALTHY,
                ]
            ).count(),
        }
        serializer = PlatformOverviewSerializer(payload)
        return Response(serializer.data)


class PlatformBlueprintView(APIView):
    def get(self, request):
        return Response(
            {
                "modules": PRIMARY_MODULES,
                "services": BACKEND_SERVICES,
                "stack": STACK_LAYERS,
                "operator_workflows": OPERATOR_WORKFLOWS,
            }
        )


class DevicesDataView(APIView):
    def get(self, request):
        try:
            return Response(get_devices_data())
        except Exception as exc:
            return Response(
                {"detail": f"Failed to fetch devices: {exc}"},
                status=500,
            )


def _latest_image_response(request, payload: dict, status_code=http_status.HTTP_200_OK):
    """JSON response with ``image_url`` / ``url`` rewritten to absolute media or S3 URLs."""
    response_payload = dict(payload or {})
    if response_payload.get("device_id") and not response_payload.get("device_uid"):
        _, resolved_uid = resolve_device_identity(response_payload.get("device_id"))
        response_payload["device_uid"] = resolved_uid
    return Response(
        normalize_latest_image_payload(request, response_payload),
        status=status_code,
    )


class LatestImageDataView(APIView):
    def get(self, request):
        """
        With ``device_id``: require a camera-service assignment (POST …/ip), then return
        the latest capture for that logical device — same rules as the camera service's
        ``GET /latest-image`` (assigned ESP32 only).

        Without ``device_id``: latest image row from the platform database (legacy).
        """
        try:
            raw_id = request.query_params.get("device_id")
            device_id = (raw_id or "").strip() or None

            if device_id:
                enc = quote(device_id, safe="")
                st_ip, body_ip = camera_service_get(f"/api/v1/devices/{enc}/ip")
                if st_ip == http_status.HTTP_404_NOT_FOUND:
                    return _latest_image_response(
                        request,
                        {
                            "image_url": None,
                            "url": None,
                            "camera_assigned": False,
                        },
                    )
                if st_ip is None:
                    # Camera microservice down / unreachable — use platform DB if we have a stored image.
                    db_row = get_latest_image_data(device_id=device_id)
                    db_url = (db_row or {}).get("image_url") or (db_row or {}).get("url")
                    if db_url:
                        return _latest_image_response(
                            request,
                            {
                                "image_url": str(db_url),
                                "url": str(db_url),
                                "camera_assigned": None,
                                "image_source": "platform_db",
                                "timestamp": db_row.get("timestamp"),
                            },
                        )
                    detail = body_ip.get("detail") if isinstance(body_ip, dict) else None
                    return _latest_image_response(
                        request,
                        {
                            "detail": detail
                            or "Camera service unreachable or error checking assignment.",
                            "camera_assigned": None,
                            "image_url": None,
                        },
                        status_code=http_status.HTTP_502_BAD_GATEWAY,
                    )

                if st_ip >= 400:
                    detail = body_ip.get("detail") if isinstance(body_ip, dict) else None
                    return _latest_image_response(
                        request,
                        {
                            "detail": detail
                            or "Camera service returned an error checking assignment.",
                            "camera_assigned": None,
                            "image_url": None,
                        },
                        status_code=http_status.HTTP_502_BAD_GATEWAY,
                    )

                st_img, body_img = camera_service_get(
                    f"/api/v1/devices/{enc}/latest-image"
                )
                if st_img == http_status.HTTP_404_NOT_FOUND:
                    return _latest_image_response(
                        request,
                        {
                            "image_url": None,
                            "url": None,
                            "camera_assigned": True,
                        },
                    )
                if st_img is None:
                    db_row = get_latest_image_data(device_id=device_id)
                    db_url = (db_row or {}).get("image_url") or (db_row or {}).get("url")
                    if db_url:
                        return _latest_image_response(
                            request,
                            {
                                "image_url": str(db_url),
                                "url": str(db_url),
                                "camera_assigned": True,
                                "image_source": "platform_db",
                                "timestamp": db_row.get("timestamp"),
                            },
                        )
                    detail = body_img.get("detail") if isinstance(body_img, dict) else None
                    return _latest_image_response(
                        request,
                        {
                            "detail": detail
                            or f"Could not load latest image (HTTP {st_img}).",
                            "camera_assigned": True,
                            "image_url": None,
                        },
                        status_code=http_status.HTTP_502_BAD_GATEWAY,
                    )
                if st_img >= 400:
                    detail = body_img.get("detail") if isinstance(body_img, dict) else None
                    return _latest_image_response(
                        request,
                        {
                            "detail": detail
                            or f"Could not load latest image (HTTP {st_img}).",
                            "camera_assigned": True,
                            "image_url": None,
                        },
                        status_code=st_img,
                    )

                payload = dict(body_img) if isinstance(body_img, dict) else {}
                payload["camera_assigned"] = True
                payload.setdefault("image_source", "camera_service")
                return _latest_image_response(request, payload)

            return _latest_image_response(request, get_latest_image_data(device_id=None))
        except Exception as exc:
            return Response(
                {"detail": f"Failed to fetch latest image: {exc}"},
                status=500,
            )


class TelemetryDataView(APIView):
    def get(self, request):
        try:
            section = request.query_params.get("section")
            device_input = request.query_params.get("device_id")
            limit = request.query_params.get("limit", 500)
            # Support section-scoped telemetry from /data endpoint as array response.
            if section and str(section).strip():
                payload = get_section_timeseries(section=section, device_id=device_input, limit=limit)
                return Response(payload)
            return Response(get_telemetry_data())
        except Exception as exc:
            return Response(
                {"detail": f"Failed to fetch telemetry data: {exc}"},
                status=500,
            )


class LocationsDataView(APIView):
    def get(self, request):
        try:
            return Response(get_locations_data())
        except Exception as exc:
            return Response(
                {"detail": f"Failed to fetch locations data: {exc}"},
                status=500,
            )


class SectionTelemetryDataView(APIView):
    def get(self, request):
        section = request.query_params.get("section")
        device_input = request.query_params.get("device_id")
        limit = request.query_params.get("limit", 20)
        try:
            resolved_device_id, resolved_device_uid = resolve_device_identity(device_input)
            payload = get_section_timeseries(section=section, device_id=device_input, limit=limit)
            return Response(
                {
                    "section": str(section or "").upper(),
                    "device_id": resolved_device_id,
                    "device_uid": resolved_device_uid,
                    "count": len(payload),
                    "results": payload,
                }
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        except Exception as exc:
            return Response(
                {"detail": f"Failed to fetch section telemetry: {exc}"},
                status=500,
            )
