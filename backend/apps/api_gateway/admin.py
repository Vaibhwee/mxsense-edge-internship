from django.contrib import admin

from .models import ApiEndpoint, ApiRequestLog, FrontendClient


admin.site.register(FrontendClient)
admin.site.register(ApiEndpoint)
admin.site.register(ApiRequestLog)
