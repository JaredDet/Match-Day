from rest_framework import serializers


class CreateMatchRequest(serializers.Serializer):
    home_team_name = serializers.CharField(max_length=200)
    away_team_name = serializers.CharField(max_length=200)
    scheduled_at = serializers.DateTimeField(input_formats=["iso-8601"])
