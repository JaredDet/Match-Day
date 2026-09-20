from rest_framework import serializers


class ListFixturesRequest(serializers.Serializer):
    phase = serializers.UUIDField(source="phase_id", required=False)
