from rest_framework import serializers


class UpdateGroupRequest(serializers.Serializer):
    name = serializers.CharField(max_length=30)
