from rest_framework import serializers

from .models import Alert, DecisionReview, DecisionRule, NotificationRoute, QualityScore


class DecisionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionRule
        fields = "__all__"


class QualityScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityScore
        fields = "__all__"


class NotificationRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRoute
        fields = "__all__"


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = "__all__"


class DecisionReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionReview
        fields = "__all__"
