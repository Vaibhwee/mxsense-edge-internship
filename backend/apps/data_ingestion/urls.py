from rest_framework.routers import DefaultRouter

from .views import (
    BatchViewSet,
    CalibrationProfileViewSet,
    CollectionSessionViewSet,
    DataValidationRuleViewSet,
    ImageCaptureViewSet,
    SampleViewSet,
    SensorReadingViewSet,
    SensorViewSet,
)


router = DefaultRouter()
router.register("validation-rules", DataValidationRuleViewSet, basename="validation-rule")
router.register("sensors", SensorViewSet, basename="sensor")
router.register("calibration-profiles", CalibrationProfileViewSet, basename="calibration-profile")
router.register("batches", BatchViewSet, basename="batch")
router.register("samples", SampleViewSet, basename="sample")
router.register("collection-sessions", CollectionSessionViewSet, basename="collection-session")
router.register("sensor-readings", SensorReadingViewSet, basename="sensor-reading")
router.register("image-captures", ImageCaptureViewSet, basename="image-capture")

urlpatterns = router.urls
