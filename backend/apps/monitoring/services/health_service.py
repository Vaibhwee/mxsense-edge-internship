from __future__ import annotations

from typing import List, Tuple

from django.utils import timezone

from apps.device_manager.models import Device
from apps.monitoring.models import AIHealthExplanation, AIHealthSummary, DeviceHealthSummary


AIReason = Tuple[str, str, str]  # (reason_code, message, severity)


def compute_ai_health(device: Device):
    health = 100.0
    reasons: List[AIReason] = []

    # TODO: Replace with actual queries (inference run tables, gating checks, etc.)
    confidence = 0.8
    channel_conflict = False
    gating_valid = True

    if not gating_valid:
        health -= 40
        reasons.append(("GATING_FAIL", "Invalid run conditions", "HIGH"))

    if confidence < 0.6:
        health -= 20
        reasons.append(("LOW_CONFIDENCE", "Confidence below threshold", "MEDIUM"))

    if channel_conflict:
        health -= 20
        reasons.append(("CHANNEL_CONFLICT", "Sensor mismatch", "MEDIUM"))

    if health >= 80:
        status = AIHealthSummary.HealthStatus.HEALTHY
    elif health >= 50:
        status = AIHealthSummary.HealthStatus.DEGRADED
    else:
        status = AIHealthSummary.HealthStatus.UNRELIABLE

    return health, status, confidence, gating_valid, reasons


def compute_device_health(device: Device):
    health = 100.0

    # TODO: Replace with actual queries (telemetry, device events, maintenance schedules, etc.)
    flow_ok = True
    fan_ok = True
    connectivity_ok = True
    maintenance_due = False

    if not flow_ok:
        health -= 30

    if not fan_ok:
        health -= 25

    if not connectivity_ok:
        health -= 15

    if maintenance_due:
        health -= 10

    if health >= 80:
        status = DeviceHealthSummary.HealthStatus.HEALTHY
    elif health >= 50:
        status = DeviceHealthSummary.HealthStatus.WARNING
    else:
        status = DeviceHealthSummary.HealthStatus.CRITICAL

    return health, status, flow_ok, fan_ok, connectivity_ok, maintenance_due


def update_ai_health(device: Device):
    score, status, confidence, gating_valid, reasons = compute_ai_health(device)

    ai_health = AIHealthSummary.objects.create(
        device=device,
        health_score=score,
        health_status=status,
        confidence_score=confidence,
        gating_valid=gating_valid,
    )

    for code, msg, severity in reasons:
        AIHealthExplanation.objects.create(
            ai_health=ai_health,
            reason_code=code,
            message=msg,
            severity=severity,
        )

    return ai_health


def update_device_health(device: Device):
    score, status, flow_ok, fan_ok, connectivity_ok, maintenance_due = compute_device_health(device)

    device_health = DeviceHealthSummary.objects.create(
        device=device,
        health_score=score,
        health_status=status,
        flow_ok=flow_ok,
        fan_ok=fan_ok,
        connectivity=1.0 if connectivity_ok else 0.5,
        maintenance=0.5 if maintenance_due else 1.0,
        last_seen=device.last_seen_at or timezone.now(),
    )

    return device_health

