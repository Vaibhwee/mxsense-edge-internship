import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Device,
    DeviceChannel,
    DeviceConfiguration,
    DeviceLifecycleEvent,
    FirmwareUpdateJob,
    Site,
)
from .serializers import (
    DeviceChannelSerializer,
    DeviceConfigurationSerializer,
    DeviceLifecycleEventSerializer,
    DeviceSerializer,
    FirmwareUpdateJobSerializer,
    SiteSerializer,
)


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related("site").all()
    serializer_class = DeviceSerializer

    @action(detail=True, methods=["post"])
    def heartbeat(self, request, pk=None):
        device = self.get_object()
        next_status = request.data.get("status", Device.DeviceStatus.ACTIVE)
        valid_statuses = {choice for choice, _ in Device.DeviceStatus.choices}

        if next_status not in valid_statuses:
            return Response(
                {"detail": "Invalid status supplied."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        details = request.data.get("details", {})
        if details and not isinstance(details, dict):
            return Response(
                {"detail": "details must be a JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        heartbeat_at = timezone.now()
        device.status = next_status
        device.last_seen_at = heartbeat_at
        device.last_heartbeat_at = heartbeat_at
        device.save()

        DeviceLifecycleEvent.objects.create(
            device=device,
            event_type=DeviceLifecycleEvent.EventType.HEARTBEAT,
            status=next_status,
            details=details or {},
        )

        return Response(self.get_serializer(device).data)


class DeviceChannelViewSet(viewsets.ModelViewSet):
    queryset = DeviceChannel.objects.select_related("device").all()
    serializer_class = DeviceChannelSerializer


class DeviceConfigurationViewSet(viewsets.ModelViewSet):
    queryset = DeviceConfiguration.objects.select_related("device").all()
    serializer_class = DeviceConfigurationSerializer


class FirmwareUpdateJobViewSet(viewsets.ModelViewSet):
    queryset = FirmwareUpdateJob.objects.select_related("device").all()
    serializer_class = FirmwareUpdateJobSerializer


class DeviceLifecycleEventViewSet(viewsets.ModelViewSet):
    queryset = DeviceLifecycleEvent.objects.select_related("device").all()
    serializer_class = DeviceLifecycleEventSerializer


class DeviceManagementActionView(APIView):
    """
    Generic entrypoint for console device-management forms.

    The frontend posts an `action` slug and free-form `payload`.
    This view maps well-known actions onto concrete device-manager
    operations so that all forms are backed by the database.
    """

    def post(self, request):
        action_slug = request.data.get("action")
        payload = request.data.get("payload") or {}

        if not action_slug:
            return Response(
                {"detail": "action is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_camera_action = action_slug in {"assign-camera", "remove-camera"}

        # Helper: resolve device by external_id/ID/name hints.
        def _resolve_device_from_payload():
            identifier = (
                payload.get("deviceId")
                or payload.get("device_id")
                or payload.get("deviceName")
                or payload.get("external_id")
            )
            if not identifier:
                return None
            # Prefer external_id match; fall back to primary key lookup.
            device = Device.objects.filter(external_id=str(identifier)).first()
            if device:
                return device
            try:
                return Device.objects.filter(pk=identifier).first()
            except Exception:
                return None

        # Special-case: "add-device" actually creates the Device row.
        if action_slug == "add-device":
            device_name = str(payload.get("deviceName") or "").strip()
            device_type = str(payload.get("deviceType") or "").strip()
            location = str(payload.get("location") or "").strip()

            if not device_name or not device_type:
                return Response(
                    {"detail": "deviceName and deviceType are required for add-device."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            external_id = device_name
            device, created = Device.objects.get_or_create(
                external_id=external_id,
                defaults={
                    "name": device_name,
                    "device_type": device_type,
                    "location": location,
                },
            )

            if not created:
                # Update basic attributes if the device already exists.
                updated = False
                if location and device.location != location:
                    device.location = location
                    updated = True
                if device.device_type != device_type:
                    device.device_type = device_type
                    updated = True
                if updated:
                    device.save()

            DeviceLifecycleEvent.objects.create(
                device=device,
                event_type=DeviceLifecycleEvent.EventType.REGISTERED,
                status=device.status,
                details={"action": action_slug, "payload": payload},
            )

            return Response(
                {
                    "action": action_slug,
                    "created": created,
                    "device": DeviceSerializer(device).data,
                },
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        # For all other actions, attach a lifecycle event if we can resolve a device.
        device = _resolve_device_from_payload()
        if device is None and not is_camera_action:
            # Still accept the call so forms are wired, but surface a clear message.
            return Response(
                {
                    "action": action_slug,
                    "detail": "No matching device found for provided identifiers.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        camera_api_base = os.getenv(
            "CAMERA_SERVICE_URL", "http://127.0.0.1:8011"
        ).rstrip("/")
        camera_result = None

        def _camera_request(method: str, path: str, body: dict | None = None):
            url = f"{camera_api_base}{path}"
            data_bytes = None
            headers = {}
            if body is not None:
                data_bytes = json.dumps(body).encode("utf-8")
                headers["Content-Type"] = "application/json"

            req = urllib.request.Request(url, method=method, data=data_bytes, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    raw = resp.read().decode("utf-8")
                    if not raw.strip():
                        return {"status": resp.status, "body": {}}
                    try:
                        return {"status": resp.status, "body": json.loads(raw)}
                    except json.JSONDecodeError:
                        return {"status": resp.status, "body": {"raw": raw}}
            except urllib.error.HTTPError as exc:
                raw = exc.read().decode("utf-8") if exc.fp else ""
                return {
                    "status": exc.code,
                    "body": {"raw": raw or str(exc)},
                }
            except Exception as exc:  # noqa: BLE001
                return {"status": None, "body": {"raw": str(exc)}}

        # Camera actions (ESP32-CAM mapping)
        if action_slug == "assign-camera":
            ip_address = payload.get("ipAddress") or payload.get("ip_address") or payload.get("esp32Ip")
            camera_label = payload.get("cameraLabel") or payload.get("camera_label") or payload.get("label")
            capture_interval = (
                payload.get("captureIntervalSeconds")
                or payload.get("capture_interval_seconds")
                or payload.get("captureInterval")
            )

            if not ip_address:
                return Response(
                    {"detail": "ipAddress is required for assign-camera."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Normalize ESP32 IP input (users might paste full URL like http://192.168.0.187).
            # Keep only host[:port], no scheme or path.
            ip_address_str = str(ip_address).strip()
            ip_address_str = re.sub(
                r"^https?://", "", ip_address_str, flags=re.IGNORECASE
            )
            ip_address_str = ip_address_str.split("/")[0].strip()

            cam_device_id = (
                str(device.external_id)
                if device is not None
                else str(
                    payload.get("deviceId")
                    or payload.get("device_id")
                    or payload.get("external_id")
                    or payload.get("deviceName")
                )
            )
            body = {"device_id": cam_device_id, "ip_address": ip_address_str}
            if camera_label is not None and str(camera_label).strip():
                body["label"] = str(camera_label).strip()

            cam_resp = _camera_request(
                "POST",
                f"/api/v1/devices/{urllib.parse.quote(cam_device_id, safe='')}/ip",
                body=body,
            )

            if cam_resp.get("status") is None:
                return Response(
                    {"detail": "Camera service request failed.", "camera": cam_resp},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            if int(cam_resp.get("status") or 0) >= 400:
                return Response(
                    {"detail": "Camera service returned an error.", "camera": cam_resp},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            camera_result = cam_resp

            # Configure periodic capture interval (global) so images refresh automatically.
            if capture_interval is not None and str(capture_interval).strip():
                try:
                    interval_seconds = int(capture_interval)
                except Exception:
                    interval_seconds = None

                if interval_seconds is not None:
                    _camera_request(
                        "POST",
                        "/api/v1/devices/scheduler/config",
                        body={"enabled": True, "interval_seconds": interval_seconds},
                    )

            # Capture immediately once so the Live Camera panel has something to display.
            initial_capture = _camera_request(
                "POST",
                f"/api/v1/devices/{cam_device_id}/capture-and-store",
                body=None,
            )
            # Do not fail the whole request if capture fails; mapping is still useful.
            if initial_capture.get("status") and int(initial_capture.get("status") or 0) < 400:
                camera_result["initial_capture"] = initial_capture
            else:
                camera_result["initial_capture"] = initial_capture

        elif action_slug == "remove-camera":
            cam_device_id = (
                str(device.external_id)
                if device is not None
                else str(
                    payload.get("deviceId")
                    or payload.get("device_id")
                    or payload.get("external_id")
                    or payload.get("deviceName")
                )
            )
            cam_resp = _camera_request(
                "DELETE",
                f"/api/v1/devices/{cam_device_id}/ip",
                body=None,
            )
            if cam_resp.get("status") is None:
                return Response(
                    {"detail": "Camera service request failed.", "camera": cam_resp},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            if int(cam_resp.get("status") or 0) >= 400:
                return Response(
                    {"detail": "Camera service returned an error.", "camera": cam_resp},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            camera_result = cam_resp

        response_payload = {
            "action": action_slug,
            "device": DeviceSerializer(device).data if device is not None else None,
        }
        if camera_result is not None:
            response_payload["camera"] = camera_result

        # Map high-level actions to coarse lifecycle event types.
        if device is not None:
            event_type_map = {
                "decommission": DeviceLifecycleEvent.EventType.DECOMMISSIONED,
                "revoke-credentials": DeviceLifecycleEvent.EventType.MAINTENANCE,
                "archive-history": DeviceLifecycleEvent.EventType.MAINTENANCE,
                "assign-camera": DeviceLifecycleEvent.EventType.MAINTENANCE,
                "remove-camera": DeviceLifecycleEvent.EventType.MAINTENANCE,
                "pause-communication": DeviceLifecycleEvent.EventType.MAINTENANCE,
                "pause-ingestion": DeviceLifecycleEvent.EventType.MAINTENANCE,
                "pause-inference": DeviceLifecycleEvent.EventType.MAINTENANCE,
                "resume-device": DeviceLifecycleEvent.EventType.MAINTENANCE,
                "assign-token": DeviceLifecycleEvent.EventType.PROVISIONED,
                "issue-certificate": DeviceLifecycleEvent.EventType.PROVISIONED,
                "bind-mqtt-topics": DeviceLifecycleEvent.EventType.PROVISIONED,
                "set-api-permissions": DeviceLifecycleEvent.EventType.PROVISIONED,
                "refresh-status": DeviceLifecycleEvent.EventType.HEARTBEAT,
                "mark-maintenance-mode": DeviceLifecycleEvent.EventType.MAINTENANCE,
                "acknowledge-fault": DeviceLifecycleEvent.EventType.MAINTENANCE,
            }

            event_type = event_type_map.get(
                action_slug, DeviceLifecycleEvent.EventType.MAINTENANCE
            )

            DeviceLifecycleEvent.objects.create(
                device=device,
                event_type=event_type,
                status=device.status,
                details={"action": action_slug, "payload": payload},
            )

        return Response(response_payload, status=status.HTTP_200_OK)
