from rest_framework import serializers


class SeasonTeamRequest(serializers.Serializer):
    team_id = serializers.UUIDField()
