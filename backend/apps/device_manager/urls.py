from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    DeviceChannelViewSet,
    DeviceConfigurationViewSet,
    DeviceLifecycleEventViewSet,
    DeviceManagementActionView,
    DeviceViewSet,
    FirmwareUpdateJobViewSet,
    SiteViewSet,
)


router = DefaultRouter()
router.register("sites", SiteViewSet, basename="site")
router.register("devices", DeviceViewSet, basename="device")
router.register("channels", DeviceChannelViewSet, basename="device-channel")
router.register("configurations", DeviceConfigurationViewSet, basename="device-configuration")
router.register("firmware-jobs", FirmwareUpdateJobViewSet, basename="firmware-job")
router.register("lifecycle-events", DeviceLifecycleEventViewSet, basename="lifecycle-event")

urlpatterns = [
    path("actions/", DeviceManagementActionView.as_view(), name="device-management-action"),
]
urlpatterns += router.urls
