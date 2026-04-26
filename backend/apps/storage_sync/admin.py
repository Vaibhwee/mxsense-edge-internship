from django.contrib import admin

from .models import BackupJob, RetentionPolicy, StorageArtifact, SyncJob


admin.site.register(StorageArtifact)
admin.site.register(RetentionPolicy)
admin.site.register(BackupJob)
admin.site.register(SyncJob)
