from rest_framework import serializers


class ListFixturesResponse(serializers.Serializer):
    id = serializers.UUIDField()
    phase = serializers.UUIDField(source="phase_id")
    group = serializers.UUIDField(source="group_id", allow_null=True)
    match = serializers.UUIDField(source="match_id")
    position = serializers.IntegerField()
    matchday = serializers.IntegerField()
