from django.contrib import admin

from .models import MqttMessageLog, ProtocolAdapter, SchemaMapping, TopicSubscription


admin.site.register(ProtocolAdapter)
admin.site.register(TopicSubscription)
admin.site.register(SchemaMapping)
admin.site.register(MqttMessageLog)
