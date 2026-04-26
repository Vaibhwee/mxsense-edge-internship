from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("ingest/", views.ingest, name="ingest"),
    path("devices/", views.devices_list, name="devices_list"),
    path("devices/<str:device_id>/", views.device_detail, name="device_detail"),
    path(
        "devices/<str:device_id>/sensor/<str:sensor_type>/",
        views.sensor_history,
        name="sensor_history",
    ),
    path("devices/<str:device_id>/health/", views.device_health_history, name="device_health_history"),
    path("dashboard/summary/", views.dashboard_summary, name="dashboard_summary"),
]

