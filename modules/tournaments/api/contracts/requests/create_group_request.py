from rest_framework import serializers


class CreateGroupRequest(serializers.Serializer):
    phase = serializers.UUIDField(source="phase_id")
    name = serializers.CharField(max_length=30)
