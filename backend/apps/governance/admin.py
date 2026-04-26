from django.contrib import admin

from .models import AccessPolicy, ApprovalRequest, AuditLog, PlatformRole, SecretCredential


admin.site.register(PlatformRole)
admin.site.register(AccessPolicy)
admin.site.register(ApprovalRequest)
admin.site.register(AuditLog)
admin.site.register(SecretCredential)
