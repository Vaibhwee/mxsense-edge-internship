from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .models import (
    AcousticData,
    DeviceHealth,
    DistanceData,
    EnvData,
    FlowData,
    ForceData,
    GasData,
    HeaderData,
    ImageMetadata,
    McuMonitoring,
    PmData,
    SensorData,
    SpectralData,
    SystemData,
    VocData,
)
from .consumers import device_group_name


def health_check(_request):
    return JsonResponse({"status": "ok"})


def _parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.now(tz=timezone.utc)
    # Supports "2026-03-17T02:05:00Z" and offsets.
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def ingest(request: Request) -> Response:
    payload: dict[str, Any] = request.data if isinstance(request.data, dict) else {}

    header = payload.get("header") or {}
    device_id = header.get("device_id") or payload.get("device_id")
    if not device_id:
        return Response({"error": "Missing device_id"}, status=status.HTTP_400_BAD_REQUEST)

    ts = _parse_timestamp(header.get("timestamp") or payload.get("timestamp"))

    HeaderData.objects.create(
        device_id=device_id,
        timestamp=ts,
        firmware_version=header.get("firmware_version"),
        location_tag=header.get("location_tag"),
    )

    mcu = payload.get("mcu_monitoring") or {}
    if mcu:
        McuMonitoring.objects.create(
            device_id=device_id,
            timestamp=ts,
            carrier_board_mcu=mcu.get("carrier_board_mcu"),
            uptime_seconds=_int(mcu.get("uptime_seconds")),
            vcc_main_v=_float(mcu.get("vcc_main_v")),
            i2c_bus_status=mcu.get("i2c_bus_status"),
            spi_bus_status=mcu.get("spi_bus_status"),
            watchdog_resets=_int(mcu.get("watchdog_resets")),
        )

    health = payload.get("device_health") or {}
    if health:
        DeviceHealth.objects.create(
            device_id=device_id,
            timestamp=ts,
            soc_temp_c=_float(health.get("soc_temp_c")),
            gpu_load_percent=_float(health.get("gpu_load_percent")),
            cpu_load_percent=health.get("cpu_load_percent"),
            ram_usage_mb=_int(health.get("ram_usage_mb")),
            emmc_storage_free_gb=_float(health.get("emmc_storage_free_gb")),
            power_mode=health.get("power_mode"),
            fan_speed_rpm=_int(health.get("fan_speed_rpm")),
        )

    sensors = payload.get("sensor_payload") or {}

    env = sensors.get("env") or {}
    if env:
        EnvData.objects.create(
            device_id=device_id,
            timestamp=ts,
            sht45_temperature=_float(env.get("sht45_temperature")),
            sht45_humidity=_float(env.get("sht45_humidity")),
            bme688_temperature=_float(env.get("bme688_temperature")),
            bme688_humidity=_float(env.get("bme688_humidity")),
            bme688_pressure=_float(env.get("bme688_pressure")),
        )

    voc = sensors.get("voc") or {}
    if voc:
        VocData.objects.create(
            device_id=device_id,
            timestamp=ts,
            sgp41_voc_index=_int(voc.get("sgp41_voc_index")),
            sgp41_nox_index=_int(voc.get("sgp41_nox_index")),
            zmod4410_voc_concentration=_float(voc.get("zmod4410_voc_concentration")),
            bme688_gas_resistance=_float(voc.get("bme688_gas_resistance")),
            tgs2602_odor_level=_float(voc.get("tgs2602_odor_level")),
        )

    gas = sensors.get("gas") or {}
    if gas:
        GasData.objects.create(
            device_id=device_id,
            timestamp=ts,
            mq135_air_quality=_float(gas.get("mq135_air_quality")),
            mq136_sulfur_level=_float(gas.get("mq136_sulfur_level")),
            tgs2600_contamination=_float(gas.get("tgs2600_contamination")),
            ethylene_sensor_value=_float(gas.get("ethylene_sensor_value")),
        )

    pm = sensors.get("pm") or {}
    if pm:
        PmData.objects.create(
            device_id=device_id,
            timestamp=ts,
            pms7003_pm1=_float(pm.get("pms7003_pm1")),
            pms7003_pm2_5=_float(pm.get("pms7003_pm2_5")),
            pms7003_pm10=_float(pm.get("pms7003_pm10")),
            sps30_pm1=_float(pm.get("sps30_pm1")),
            sps30_pm2_5=_float(pm.get("sps30_pm2_5")),
            sps30_pm10=_float(pm.get("sps30_pm10")),
        )

    spectral = sensors.get("spectral") or {}
    if spectral:
        SpectralData.objects.create(
            device_id=device_id,
            timestamp=ts,
            as7341_channels=spectral.get("as7341_channels"),
            as7265x_channels=spectral.get("as7265x_channels"),
        )

    force = sensors.get("force") or {}
    if force:
        ForceData.objects.create(
            device_id=device_id,
            timestamp=ts,
            loadcell_2kg_force=_float(force.get("loadcell_2kg_force")),
            loadcell_5kg_force=_float(force.get("loadcell_5kg_force")),
        )

    flow = sensors.get("flow") or {}
    if flow:
        FlowData.objects.create(
            device_id=device_id,
            timestamp=ts,
            mpxv7002dp_pressure_diff=_float(flow.get("mpxv7002dp_pressure_diff")),
            sfm3003_flow_rate=_float(flow.get("sfm3003_flow_rate")),
        )

    system = sensors.get("system") or {}
    if system:
        SystemData.objects.create(
            device_id=device_id,
            timestamp=ts,
            ds18b20_temperature=_float(system.get("ds18b20_temperature")),
            ina219_current=_float(system.get("ina219_current")),
            ina219_power=_float(system.get("ina219_power")),
            reed_switch_state=system.get("reed_switch_state"),
        )

    acoustic = sensors.get("acoustic") or {}
    if acoustic:
        AcousticData.objects.create(
            device_id=device_id,
            timestamp=ts,
            inmp441_noise_level=_float(acoustic.get("inmp441_noise_level")),
        )

    distance = sensors.get("distance") or {}
    if distance:
        DistanceData.objects.create(
            device_id=device_id,
            timestamp=ts,
            vl53l1x_fill_height=_float(distance.get("vl53l1x_fill_height")),
        )

    image = payload.get("image_metadata") or {}
    if image:
        ImageMetadata.objects.create(
            device_id=device_id,
            timestamp=ts,
            camera_id=image.get("camera_id"),
            frame_id=_int(image.get("frame_id")),
            resolution=image.get("resolution"),
            format=image.get("format"),
            storage_path=image.get("storage_path"),
            inference_applied=image.get("inference_applied"),
            detected_objects=image.get("detected_objects"),
        )

    SensorData.objects.create(device_id=device_id, timestamp=ts, payload=payload)

    channel_layer = get_channel_layer()
    if channel_layer is not None:
        data = _ws_data(device_id, ts, payload)
        async_to_sync(channel_layer.group_send)("dashboard", {"type": "telemetry", "data": data})
        async_to_sync(channel_layer.group_send)(device_group_name(device_id), {"type": "telemetry", "data": data})

    return Response({"status": "ingested"}, status=status.HTTP_201_CREATED)


def _model_to_dict(obj: Any, fields: list[str]) -> dict[str, Any] | None:
    if obj is None:
        return None
    data: dict[str, Any] = {}
    for f in fields:
        v = getattr(obj, f, None)
        if isinstance(v, datetime):
            data[f] = v.isoformat()
        else:
            data[f] = v
    return data


def _system_row_from_health(obj: DeviceHealth | None) -> dict[str, Any] | None:
    if obj is None:
        return None
    return {
        "device_id": obj.device_id,
        "timestamp": obj.timestamp.isoformat(),
        "cpu_temp": obj.soc_temp_c,
        "gpu_load": obj.gpu_load_percent,
        "ram_usage": obj.ram_usage_mb,
        "fan_speed": obj.fan_speed_rpm,
    }


def _distance_row(obj: DistanceData | None) -> dict[str, Any] | None:
    if obj is None:
        return None
    return {
        "device_id": obj.device_id,
        "timestamp": obj.timestamp.isoformat(),
        "value": obj.vl53l1x_fill_height,
    }


def _ws_data(device_id: str, ts: datetime, payload: dict[str, Any]) -> dict[str, Any]:
    sensor_payload = payload.get("sensor_payload") or {}
    health = payload.get("device_health") or {}
    return {
        "device_id": device_id,
        "timestamp": ts.isoformat(),
        "payload": payload,
        "env": sensor_payload.get("env") or {},
        "voc": sensor_payload.get("voc") or {},
        "gas": sensor_payload.get("gas") or {},
        "pm": sensor_payload.get("pm") or {},
        "system": {
            "cpu_temp": _float(health.get("soc_temp_c")),
            "gpu_load": _float(health.get("gpu_load_percent")),
            "ram_usage": _int(health.get("ram_usage_mb")),
            "fan_speed": _int(health.get("fan_speed_rpm")),
        },
        "distance": {
            "value": _float(((sensor_payload.get("distance") or {}).get("vl53l1x_fill_height"))),
        },
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def devices_list(_request: Request) -> Response:
    device_ids = list(
        HeaderData.objects.values_list("device_id", flat=True).distinct().order_by("device_id")
    )
    if not device_ids:
        device_ids = list(
            SensorData.objects.values_list("device_id", flat=True).distinct().order_by("device_id")
        )
    return Response({"devices": device_ids})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_detail(_request: Request, device_id: str) -> Response:
    header = HeaderData.objects.filter(device_id=device_id).order_by("-timestamp").first()
    mcu = McuMonitoring.objects.filter(device_id=device_id).order_by("-timestamp").first()
    health = DeviceHealth.objects.filter(device_id=device_id).order_by("-timestamp").first()

    latest = {
        "env": EnvData.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "voc": VocData.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "gas": GasData.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "pm": PmData.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "spectral": SpectralData.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "force": ForceData.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "flow": FlowData.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "system": DeviceHealth.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "acoustic": AcousticData.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "distance": DistanceData.objects.filter(device_id=device_id).order_by("-timestamp").first(),
        "image_metadata": ImageMetadata.objects.filter(device_id=device_id).order_by("-timestamp").first(),
    }

    return Response(
        {
            "device_id": device_id,
            "header": _model_to_dict(
                header, ["device_id", "timestamp", "firmware_version", "location_tag"]
            ),
            "mcu_monitoring": _model_to_dict(
                mcu,
                [
                    "device_id",
                    "timestamp",
                    "carrier_board_mcu",
                    "uptime_seconds",
                    "vcc_main_v",
                    "i2c_bus_status",
                    "spi_bus_status",
                    "watchdog_resets",
                ],
            ),
            "device_health": _model_to_dict(
                health,
                [
                    "device_id",
                    "timestamp",
                    "soc_temp_c",
                    "gpu_load_percent",
                    "cpu_load_percent",
                    "ram_usage_mb",
                    "emmc_storage_free_gb",
                    "power_mode",
                    "fan_speed_rpm",
                ],
            ),
            "latest_sensors": {
                "env": _model_to_dict(
                    latest["env"],
                    [
                        "device_id",
                        "timestamp",
                        "sht45_temperature",
                        "sht45_humidity",
                        "bme688_temperature",
                        "bme688_humidity",
                        "bme688_pressure",
                    ],
                ),
                "voc": _model_to_dict(
                    latest["voc"],
                    [
                        "device_id",
                        "timestamp",
                        "sgp41_voc_index",
                        "sgp41_nox_index",
                        "zmod4410_voc_concentration",
                        "bme688_gas_resistance",
                        "tgs2602_odor_level",
                    ],
                ),
                "gas": _model_to_dict(
                    latest["gas"],
                    [
                        "device_id",
                        "timestamp",
                        "mq135_air_quality",
                        "mq136_sulfur_level",
                        "tgs2600_contamination",
                        "ethylene_sensor_value",
                    ],
                ),
                "pm": _model_to_dict(
                    latest["pm"],
                    [
                        "device_id",
                        "timestamp",
                        "pms7003_pm1",
                        "pms7003_pm2_5",
                        "pms7003_pm10",
                        "sps30_pm1",
                        "sps30_pm2_5",
                        "sps30_pm10",
                    ],
                ),
                "spectral": _model_to_dict(latest["spectral"], ["device_id", "timestamp", "as7341_channels", "as7265x_channels"]),
                "force": _model_to_dict(latest["force"], ["device_id", "timestamp", "loadcell_2kg_force", "loadcell_5kg_force"]),
                "flow": _model_to_dict(latest["flow"], ["device_id", "timestamp", "mpxv7002dp_pressure_diff", "sfm3003_flow_rate"]),
                "system": _system_row_from_health(latest["system"]),
                "acoustic": _model_to_dict(latest["acoustic"], ["device_id", "timestamp", "inmp441_noise_level"]),
                "distance": _distance_row(latest["distance"]),
                "image_metadata": _model_to_dict(
                    latest["image_metadata"],
                    [
                        "device_id",
                        "timestamp",
                        "camera_id",
                        "frame_id",
                        "resolution",
                        "format",
                        "storage_path",
                        "inference_applied",
                        "detected_objects",
                    ],
                ),
            },
        }
    )


def _apply_time_filter(qs, start: str | None, end: str | None):
    if start:
        qs = qs.filter(timestamp__gte=_parse_timestamp(start))
    if end:
        qs = qs.filter(timestamp__lte=_parse_timestamp(end))
    return qs


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sensor_history(request: Request, device_id: str, sensor_type: str) -> Response:
    model_map = {
        "env": (EnvData, ["timestamp", "sht45_temperature", "sht45_humidity", "bme688_temperature", "bme688_humidity", "bme688_pressure"]),
        "voc": (VocData, ["timestamp", "sgp41_voc_index", "sgp41_nox_index", "zmod4410_voc_concentration", "bme688_gas_resistance", "tgs2602_odor_level"]),
        "gas": (GasData, ["timestamp", "mq135_air_quality", "mq136_sulfur_level", "tgs2600_contamination", "ethylene_sensor_value"]),
        "pm": (PmData, ["timestamp", "pms7003_pm1", "pms7003_pm2_5", "pms7003_pm10", "sps30_pm1", "sps30_pm2_5", "sps30_pm10"]),
        "spectral": (SpectralData, ["timestamp", "as7341_channels", "as7265x_channels"]),
        "force": (ForceData, ["timestamp", "loadcell_2kg_force", "loadcell_5kg_force"]),
        "flow": (FlowData, ["timestamp", "mpxv7002dp_pressure_diff", "sfm3003_flow_rate"]),
        "acoustic": (AcousticData, ["timestamp", "inmp441_noise_level"]),
    }
    limit = min(int(request.query_params.get("limit", "200")), 5000)
    start = request.query_params.get("start")
    end = request.query_params.get("end")

    if sensor_type == "system":
        qs = DeviceHealth.objects.filter(device_id=device_id).order_by("-timestamp")
        qs = _apply_time_filter(qs, start, end)
        rows = []
        for obj in qs[:limit]:
            row = _system_row_from_health(obj)
            if row:
                rows.append(row)
        rows.reverse()
        return Response({"device_id": device_id, "type": sensor_type, "rows": rows})

    if sensor_type == "distance":
        qs = DistanceData.objects.filter(device_id=device_id).order_by("-timestamp")
        qs = _apply_time_filter(qs, start, end)
        rows = []
        for obj in qs[:limit]:
            row = _distance_row(obj)
            if row:
                rows.append(row)
        rows.reverse()
        return Response({"device_id": device_id, "type": sensor_type, "rows": rows})

    if sensor_type not in model_map:
        return Response({"error": f"Unknown sensor type: {sensor_type}"}, status=status.HTTP_400_BAD_REQUEST)

    model, fields = model_map[sensor_type]
    qs = model.objects.filter(device_id=device_id).order_by("-timestamp")
    qs = _apply_time_filter(qs, start, end)
    rows = []
    for obj in qs[:limit]:
        row = _model_to_dict(obj, ["device_id"] + fields)
        if row:
            rows.append(row)

    rows.reverse()
    return Response({"device_id": device_id, "type": sensor_type, "rows": rows})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_health_history(request: Request, device_id: str) -> Response:
    limit = min(int(request.query_params.get("limit", "200")), 5000)
    start = request.query_params.get("start")
    end = request.query_params.get("end")

    qs = DeviceHealth.objects.filter(device_id=device_id).order_by("-timestamp")
    qs = _apply_time_filter(qs, start, end)
    rows = []
    for obj in qs[:limit]:
        row = _model_to_dict(
            obj,
            [
                "device_id",
                "timestamp",
                "soc_temp_c",
                "gpu_load_percent",
                "cpu_load_percent",
                "ram_usage_mb",
                "emmc_storage_free_gb",
                "power_mode",
                "fan_speed_rpm",
            ],
        )
        if row:
            rows.append(row)
    rows.reverse()
    return Response({"device_id": device_id, "rows": rows})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(_request: Request) -> Response:
    device_ids = list(HeaderData.objects.values_list("device_id", flat=True).distinct())
    summary = []
    for device_id in sorted(device_ids):
        header = HeaderData.objects.filter(device_id=device_id).order_by("-timestamp").first()
        health = DeviceHealth.objects.filter(device_id=device_id).order_by("-timestamp").first()
        env = EnvData.objects.filter(device_id=device_id).order_by("-timestamp").first()
        gas = GasData.objects.filter(device_id=device_id).order_by("-timestamp").first()
        voc = VocData.objects.filter(device_id=device_id).order_by("-timestamp").first()
        pm = PmData.objects.filter(device_id=device_id).order_by("-timestamp").first()

        summary.append(
            {
                "device_id": device_id,
                "timestamp": (header.timestamp.isoformat() if header else None),
                "location_tag": (header.location_tag if header else None),
                "health": _model_to_dict(
                    health,
                    ["soc_temp_c", "gpu_load_percent", "ram_usage_mb", "fan_speed_rpm", "power_mode"],
                ),
                "env": _model_to_dict(env, ["sht45_temperature", "sht45_humidity"]),
                "gas": _model_to_dict(gas, ["mq135_air_quality", "mq136_sulfur_level"]),
                "voc": _model_to_dict(voc, ["sgp41_voc_index", "sgp41_nox_index"]),
                "pm": _model_to_dict(pm, ["pms7003_pm2_5", "pms7003_pm10"]),
            }
        )
    return Response({"devices": summary})
