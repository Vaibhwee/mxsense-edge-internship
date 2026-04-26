from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AccessPolicy, ApprovalRequest, AuditLog, PlatformRole, SecretCredential
from .serializers import (
    AccessPolicySerializer,
    ApprovalRequestSerializer,
    AuditLogSerializer,
    PlatformRoleSerializer,
    SecretCredentialSerializer,
)


class PlatformRoleViewSet(viewsets.ModelViewSet):
    queryset = PlatformRole.objects.all()
    serializer_class = PlatformRoleSerializer


class AccessPolicyViewSet(viewsets.ModelViewSet):
    queryset = AccessPolicy.objects.all()
    serializer_class = AccessPolicySerializer


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.select_related("requested_by").all()
    serializer_class = ApprovalRequestSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        approval = self.get_object()
        approval.status = ApprovalRequest.RequestStatus.APPROVED
        approval.approved_at = timezone.now()
        approval.save()
        return Response(self.get_serializer(approval).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        approval = self.get_object()
        approval.status = ApprovalRequest.RequestStatus.REJECTED
        approval.save()
        return Response(self.get_serializer(approval).data)


class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogSerializer


class SecretCredentialViewSet(viewsets.ModelViewSet):
    queryset = SecretCredential.objects.all()
    serializer_class = SecretCredentialSerializer
