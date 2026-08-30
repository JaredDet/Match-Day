from rest_framework import serializers


class CreateMatchRequest(serializers.Serializer):
    home_team_id = serializers.UUIDField()
    away_team_id = serializers.UUIDField()
    scheduled_at = serializers.DateTimeField(input_formats=["iso-8601"])
