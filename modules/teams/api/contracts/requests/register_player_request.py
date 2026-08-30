from rest_framework import serializers


class RegisterPlayerRequest(serializers.Serializer):
    name = serializers.CharField(max_length=200)
