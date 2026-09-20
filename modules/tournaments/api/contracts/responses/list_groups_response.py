from rest_framework import serializers


class ListGroupsResponse(serializers.Serializer):
    id = serializers.UUIDField()
    phase = serializers.UUIDField(source="phase_id")
    name = serializers.CharField()
    tie_break_order = serializers.ListField(child=serializers.UUIDField())
