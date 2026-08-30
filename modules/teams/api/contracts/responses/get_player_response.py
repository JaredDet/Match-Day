from rest_framework import serializers

from modules.teams.application.queries.list_teams_query import TeamMatchResult


class PlayerTeamDetailResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class PlayerStatisticsResponse(serializers.Serializer):
    appearances = serializers.IntegerField()
    goals = serializers.IntegerField()
    yellow_cards = serializers.IntegerField()
    red_cards = serializers.IntegerField()


class PlayerRecentMatchResponse(serializers.Serializer):
    match_id = serializers.UUIDField()
    scheduled_at = serializers.DateTimeField()
    opponent = PlayerTeamDetailResponse()
    result = serializers.ChoiceField(
        choices=[(result.value, result.value) for result in TeamMatchResult]
    )
    goals = serializers.IntegerField()
    yellow_cards = serializers.IntegerField()
    red_cards = serializers.IntegerField()


class GetPlayerResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    team = PlayerTeamDetailResponse()
    is_captain = serializers.BooleanField()
    statistics = PlayerStatisticsResponse()
    recent_matches = PlayerRecentMatchResponse(many=True)
