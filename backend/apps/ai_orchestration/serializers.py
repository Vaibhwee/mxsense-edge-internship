from rest_framework import serializers

from .models import (
    FeatureVector,
    InferenceJob,
    InferenceResult,
    ModelArtifact,
    PreprocessingProfile,
    ProcessedRecord,
)


class PreprocessingProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreprocessingProfile
        fields = "__all__"


class ProcessedRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedRecord
        fields = "__all__"


class FeatureVectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureVector
        fields = "__all__"


class ModelArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelArtifact
        fields = "__all__"


class InferenceJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = InferenceJob
        fields = "__all__"


class InferenceResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = InferenceResult
        fields = "__all__"
