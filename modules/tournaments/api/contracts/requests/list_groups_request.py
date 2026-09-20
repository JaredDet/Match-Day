from rest_framework import serializers


class ListGroupsRequest(serializers.Serializer):
    phase = serializers.UUIDField(source="phase_id", required=False)
