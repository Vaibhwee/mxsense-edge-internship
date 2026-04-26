from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    FeatureVector,
    InferenceJob,
    InferenceResult,
    ModelArtifact,
    PreprocessingProfile,
    ProcessedRecord,
)
from .serializers import (
    FeatureVectorSerializer,
    InferenceJobSerializer,
    InferenceResultSerializer,
    ModelArtifactSerializer,
    PreprocessingProfileSerializer,
    ProcessedRecordSerializer,
)


class PreprocessingProfileViewSet(viewsets.ModelViewSet):
    queryset = PreprocessingProfile.objects.all()
    serializer_class = PreprocessingProfileSerializer


class ProcessedRecordViewSet(viewsets.ModelViewSet):
    queryset = ProcessedRecord.objects.select_related(
        "sample",
        "session",
        "preprocessing_profile",
    ).all()
    serializer_class = ProcessedRecordSerializer


class FeatureVectorViewSet(viewsets.ModelViewSet):
    queryset = FeatureVector.objects.select_related("sample", "processed_record").all()
    serializer_class = FeatureVectorSerializer


class ModelArtifactViewSet(viewsets.ModelViewSet):
    queryset = ModelArtifact.objects.all()
    serializer_class = ModelArtifactSerializer


class InferenceJobViewSet(viewsets.ModelViewSet):
    queryset = InferenceJob.objects.select_related(
        "sample",
        "feature_vector",
        "model",
        "requested_by",
    ).all()
    serializer_class = InferenceJobSerializer

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        job = self.get_object()
        job.status = InferenceJob.JobStatus.QUEUED
        job.started_at = None
        job.completed_at = None
        job.request_metadata = {
            **job.request_metadata,
            "retried_at": timezone.now().isoformat(),
        }
        job.save()
        return Response(self.get_serializer(job).data)


class InferenceResultViewSet(viewsets.ModelViewSet):
    queryset = InferenceResult.objects.select_related("job").all()
    serializer_class = InferenceResultSerializer
