from rest_framework import serializers


class ListSeasonsResponse(serializers.Serializer):
    id = serializers.UUIDField()
    tournament = serializers.UUIDField(source="tournament_id")
    name = serializers.CharField()
    teams = serializers.ListField(child=serializers.UUIDField(), source="team_ids")
