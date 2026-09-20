from rest_framework import serializers


class CreateSeasonRequest(serializers.Serializer):
    tournament = serializers.UUIDField(source="tournament_id")
    name = serializers.CharField(max_length=30)
    teams = serializers.ListField(child=serializers.UUIDField(), source="team_ids", required=False)
