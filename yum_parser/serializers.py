from rest_framework import serializers

class PackageSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)

class PackageResponseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    nevra = serializers.CharField(max_length=255)
    version = serializers.CharField(max_length=255)
    release = serializers.CharField(max_length=255)
    url = serializers.CharField(max_length=255)