from rest_framework import viewsets

from .models import MqttMessageLog, ProtocolAdapter, SchemaMapping, TopicSubscription
from .serializers import (
    MqttMessageLogSerializer,
    ProtocolAdapterSerializer,
    SchemaMappingSerializer,
    TopicSubscriptionSerializer,
)


class ProtocolAdapterViewSet(viewsets.ModelViewSet):
    queryset = ProtocolAdapter.objects.all()
    serializer_class = ProtocolAdapterSerializer


class TopicSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = TopicSubscription.objects.select_related("adapter").all()
    serializer_class = TopicSubscriptionSerializer


class SchemaMappingViewSet(viewsets.ModelViewSet):
    queryset = SchemaMapping.objects.select_related("adapter").all()
    serializer_class = SchemaMappingSerializer


class MqttMessageLogViewSet(viewsets.ModelViewSet):
    queryset = MqttMessageLog.objects.select_related(
        "subscription",
        "device",
    ).all()
    serializer_class = MqttMessageLogSerializer
