from rest_framework.routers import DefaultRouter

from .views import (
    AlertViewSet,
    DecisionReviewViewSet,
    DecisionRuleViewSet,
    NotificationRouteViewSet,
    QualityScoreViewSet,
)


router = DefaultRouter()
router.register("decision-rules", DecisionRuleViewSet, basename="decision-rule")
router.register("quality-scores", QualityScoreViewSet, basename="quality-score")
router.register("notification-routes", NotificationRouteViewSet, basename="notification-route")
router.register("alerts", AlertViewSet, basename="alert")
router.register("decision-reviews", DecisionReviewViewSet, basename="decision-review")

urlpatterns = router.urls
