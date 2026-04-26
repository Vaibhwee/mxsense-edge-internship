from django.contrib import admin

from .models import IncidentCase, MetricSnapshot, PlatformLog, ServiceHealthCheck, TelemetryRecord


admin.site.register(ServiceHealthCheck)
admin.site.register(TelemetryRecord)
admin.site.register(MetricSnapshot)
admin.site.register(PlatformLog)
admin.site.register(IncidentCase)
