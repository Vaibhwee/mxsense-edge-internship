from django.contrib import admin

from .models import (
    FeatureVector,
    InferenceJob,
    InferenceResult,
    ModelArtifact,
    PreprocessingProfile,
    ProcessedRecord,
)


admin.site.register(PreprocessingProfile)
admin.site.register(ProcessedRecord)
admin.site.register(FeatureVector)
admin.site.register(ModelArtifact)
admin.site.register(InferenceJob)
admin.site.register(InferenceResult)
