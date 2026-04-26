from django.contrib import admin

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


admin.site.register(DataValidationRule)
admin.site.register(Sensor)
admin.site.register(CalibrationProfile)
admin.site.register(Batch)
admin.site.register(Sample)
admin.site.register(CollectionSession)
admin.site.register(SensorReading)
admin.site.register(ImageCapture)
