from rest_framework import viewsets

from .models import BackupJob, RetentionPolicy, StorageArtifact, SyncJob
from .serializers import (
    BackupJobSerializer,
    RetentionPolicySerializer,
    StorageArtifactSerializer,
    SyncJobSerializer,
)


class StorageArtifactViewSet(viewsets.ModelViewSet):
    queryset = StorageArtifact.objects.select_related("sample", "device").all()
    serializer_class = StorageArtifactSerializer


class RetentionPolicyViewSet(viewsets.ModelViewSet):
    queryset = RetentionPolicy.objects.all()
    serializer_class = RetentionPolicySerializer


class BackupJobViewSet(viewsets.ModelViewSet):
    queryset = BackupJob.objects.all()
    serializer_class = BackupJobSerializer


class SyncJobViewSet(viewsets.ModelViewSet):
    queryset = SyncJob.objects.all()
    serializer_class = SyncJobSerializer
