from rest_framework import serializers

from .models import BackupJob, RetentionPolicy, StorageArtifact, SyncJob


class StorageArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageArtifact
        fields = "__all__"


class RetentionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RetentionPolicy
        fields = "__all__"


class BackupJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupJob
        fields = "__all__"


class SyncJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncJob
        fields = "__all__"
