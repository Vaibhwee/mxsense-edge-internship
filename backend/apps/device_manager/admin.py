from django.contrib import admin

from .models import (
    Device,
    DeviceChannel,
    DeviceConfiguration,
    DeviceLifecycleEvent,
    FirmwareUpdateJob,
    Site,
)


admin.site.register(Site)
admin.site.register(Device)
admin.site.register(DeviceChannel)
admin.site.register(DeviceConfiguration)
admin.site.register(FirmwareUpdateJob)
admin.site.register(DeviceLifecycleEvent)
