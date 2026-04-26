from rest_framework.routers import DefaultRouter

from .views import (
    FeatureVectorViewSet,
    InferenceJobViewSet,
    InferenceResultViewSet,
    ModelArtifactViewSet,
    PreprocessingProfileViewSet,
    ProcessedRecordViewSet,
)


router = DefaultRouter()
router.register("preprocessing-profiles", PreprocessingProfileViewSet, basename="preprocessing-profile")
router.register("processed-records", ProcessedRecordViewSet, basename="processed-record")
router.register("feature-vectors", FeatureVectorViewSet, basename="feature-vector")
router.register("model-artifacts", ModelArtifactViewSet, basename="model-artifact")
router.register("inference-jobs", InferenceJobViewSet, basename="inference-job")
router.register("inference-results", InferenceResultViewSet, basename="inference-result")

urlpatterns = router.urls
