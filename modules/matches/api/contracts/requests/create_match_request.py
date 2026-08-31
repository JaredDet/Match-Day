from rest_framework import serializers

from core.constants import NAME_MAX_LENGTH


class CreateMatchRequest(serializers.Serializer):
    home_team_id = serializers.UUIDField()
    away_team_id = serializers.UUIDField()
    scheduled_at = serializers.DateTimeField(input_formats=["iso-8601"])
    stadium_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    referee_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
