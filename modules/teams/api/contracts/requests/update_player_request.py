from rest_framework import serializers


class UpdatePlayerRequest(serializers.Serializer):
    name = serializers.CharField(max_length=200)
