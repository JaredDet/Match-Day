from rest_framework import serializers

from modules.teams.domain.player import PlayerPosition


class PlayerTeamSummaryResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class ListPlayersResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    preferred_position = serializers.ChoiceField(
        choices=PlayerPosition.choices,
        allow_null=True,
    )
    preferred_shirt_number = serializers.IntegerField(allow_null=True)
    team = PlayerTeamSummaryResponse()
    is_captain = serializers.BooleanField()
    appearances = serializers.IntegerField()
    goals = serializers.IntegerField()
