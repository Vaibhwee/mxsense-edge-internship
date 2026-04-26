from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)
    password = serializers.CharField(required=True, allow_blank=False, write_only=True)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False, max_length=150, trim_whitespace=True)
    password = serializers.CharField(required=True, allow_blank=False, write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    full_name = serializers.CharField(required=False, allow_blank=True, default="", max_length=150)
