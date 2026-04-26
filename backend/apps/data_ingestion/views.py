from rest_framework import viewsets

from .models import (
    Batch,
    CalibrationProfile,
    CollectionSession,
    DataValidationRule,
    ImageCapture,
    Sample,
    Sensor,
    SensorReading,
)
from .serializers import (
    BatchSerializer,
    CalibrationProfileSerializer,
    CollectionSessionSerializer,
    DataValidationRuleSerializer,
    ImageCaptureSerializer,
    SampleSerializer,
    SensorReadingSerializer,
    SensorSerializer,
)


class DataValidationRuleViewSet(viewsets.ModelViewSet):
    queryset = DataValidationRule.objects.all()
    serializer_class = DataValidationRuleSerializer


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.select_related("device").all()
    serializer_class = SensorSerializer


class CalibrationProfileViewSet(viewsets.ModelViewSet):
    queryset = CalibrationProfile.objects.all()
    serializer_class = CalibrationProfileSerializer


class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer


class SampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.select_related("batch", "site", "device", "operator").all()
    serializer_class = SampleSerializer


class CollectionSessionViewSet(viewsets.ModelViewSet):
    queryset = CollectionSession.objects.select_related("device", "batch", "sample").all()
    serializer_class = CollectionSessionSerializer


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.select_related(
        "device",
        "sample",
        "session",
        "sensor",
    ).all()
    serializer_class = SensorReadingSerializer


class ImageCaptureViewSet(viewsets.ModelViewSet):
    queryset = ImageCapture.objects.select_related("sample", "session", "device").all()
    serializer_class = ImageCaptureSerializer
