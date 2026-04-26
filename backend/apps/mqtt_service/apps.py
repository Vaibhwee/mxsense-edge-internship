from django.apps import AppConfig


class MqttServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mqtt_service"
    verbose_name = "MQTT Service"
