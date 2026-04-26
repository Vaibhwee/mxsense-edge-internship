from rest_framework.routers import DefaultRouter

from .views import (
    BackupJobViewSet,
    RetentionPolicyViewSet,
    StorageArtifactViewSet,
    SyncJobViewSet,
)


router = DefaultRouter()
router.register("storage-artifacts", StorageArtifactViewSet, basename="storage-artifact")
router.register("retention-policies", RetentionPolicyViewSet, basename="retention-policy")
router.register("backup-jobs", BackupJobViewSet, basename="backup-job")
router.register("sync-jobs", SyncJobViewSet, basename="sync-job")

urlpatterns = router.urls
