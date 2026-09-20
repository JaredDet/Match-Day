from rest_framework import serializers


class CreateFixtureRequest(serializers.Serializer):
    phase = serializers.UUIDField(source="phase_id")
    group = serializers.UUIDField(source="group_id", required=False, allow_null=True)
    match = serializers.UUIDField(source="match_id")
    position = serializers.IntegerField(min_value=0, max_value=32767)
    matchday = serializers.IntegerField(min_value=1, max_value=32767, required=False)
