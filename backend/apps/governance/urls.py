from rest_framework.routers import DefaultRouter

from .views import (
    AccessPolicyViewSet,
    ApprovalRequestViewSet,
    AuditLogViewSet,
    PlatformRoleViewSet,
    SecretCredentialViewSet,
)


router = DefaultRouter()
router.register("roles", PlatformRoleViewSet, basename="platform-role")
router.register("policies", AccessPolicyViewSet, basename="access-policy")
router.register("approval-requests", ApprovalRequestViewSet, basename="approval-request")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")
router.register("secret-credentials", SecretCredentialViewSet, basename="secret-credential")

urlpatterns = router.urls
