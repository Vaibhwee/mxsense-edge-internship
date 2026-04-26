from rest_framework.routers import DefaultRouter

from .views import (
    MqttMessageLogViewSet,
    ProtocolAdapterViewSet,
    SchemaMappingViewSet,
    TopicSubscriptionViewSet,
)


router = DefaultRouter()
router.register("protocol-adapters", ProtocolAdapterViewSet, basename="protocol-adapter")
router.register("topic-subscriptions", TopicSubscriptionViewSet, basename="topic-subscription")
router.register("schema-mappings", SchemaMappingViewSet, basename="schema-mapping")
router.register("message-logs", MqttMessageLogViewSet, basename="message-log")

urlpatterns = router.urls
