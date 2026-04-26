from rest_framework import serializers

from .models import AccessPolicy, ApprovalRequest, AuditLog, PlatformRole, SecretCredential


class PlatformRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformRole
        fields = "__all__"


class AccessPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPolicy
        fields = "__all__"


class ApprovalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequest
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"


class SecretCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecretCredential
        fields = "__all__"
