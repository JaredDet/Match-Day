from rest_framework import serializers

from modules.teams.application.queries.list_teams_query import TeamMatchResult
from modules.teams.domain.player import PlayerPosition


class TeamStatisticsResponse(serializers.Serializer):
    matches_played = serializers.IntegerField()
    wins = serializers.IntegerField()
    draws = serializers.IntegerField()
    losses = serializers.IntegerField()
    goals_for = serializers.IntegerField()
    goals_against = serializers.IntegerField()


class TeamPlayerDetailResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    preferred_position = serializers.ChoiceField(
        choices=PlayerPosition.choices,
        allow_null=True,
    )
    preferred_shirt_number = serializers.IntegerField(allow_null=True)
    is_captain = serializers.BooleanField()


class TeamRecentMatchResponse(serializers.Serializer):
    match_id = serializers.UUIDField()
    opponent_name = serializers.CharField()
    scheduled_at = serializers.DateTimeField()
    goals_for = serializers.IntegerField()
    goals_against = serializers.IntegerField()
    result = serializers.ChoiceField(
        choices=[(result.value, result.value) for result in TeamMatchResult]
    )


class GetTeamResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    statistics = TeamStatisticsResponse()
    players = TeamPlayerDetailResponse(many=True)
    recent_matches = TeamRecentMatchResponse(many=True)
