from rest_framework import serializers


class UpdateFixtureRequest(serializers.Serializer):
    group = serializers.UUIDField(source="group_id", allow_null=True, required=False)
    match = serializers.UUIDField(source="match_id", required=False)
    position = serializers.IntegerField(min_value=0, max_value=32767, required=False)
    matchday = serializers.IntegerField(min_value=1, max_value=32767, required=False)
