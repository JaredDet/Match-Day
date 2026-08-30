from rest_framework import serializers


class PlayerTeamSummaryResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class ListPlayersResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    team = PlayerTeamSummaryResponse()
    is_captain = serializers.BooleanField()
    appearances = serializers.IntegerField()
    goals = serializers.IntegerField()
