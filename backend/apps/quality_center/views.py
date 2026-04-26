from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Alert, DecisionReview, DecisionRule, NotificationRoute, QualityScore
from .serializers import (
    AlertSerializer,
    DecisionReviewSerializer,
    DecisionRuleSerializer,
    NotificationRouteSerializer,
    QualityScoreSerializer,
)


class DecisionRuleViewSet(viewsets.ModelViewSet):
    queryset = DecisionRule.objects.all()
    serializer_class = DecisionRuleSerializer


class QualityScoreViewSet(viewsets.ModelViewSet):
    queryset = QualityScore.objects.select_related("sample", "inference_result").all()
    serializer_class = QualityScoreSerializer


class NotificationRouteViewSet(viewsets.ModelViewSet):
    queryset = NotificationRoute.objects.all()
    serializer_class = NotificationRouteSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related("device", "sample", "route", "acknowledged_by").all()
    serializer_class = AlertSerializer

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = Alert.AlertStatus.ACKNOWLEDGED
        if request.user and request.user.is_authenticated:
            alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        return Response(self.get_serializer(alert).data)


class DecisionReviewViewSet(viewsets.ModelViewSet):
    queryset = DecisionReview.objects.select_related(
        "sample",
        "quality_score",
        "reviewer",
    ).all()
    serializer_class = DecisionReviewSerializer
