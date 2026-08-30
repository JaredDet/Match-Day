from rest_framework import serializers

from modules.teams.application.queries.list_teams_query import TeamMatchResult


class TeamLastMatchResponse(serializers.Serializer):
    match_id = serializers.UUIDField()
    opponent_name = serializers.CharField()
    goals_for = serializers.IntegerField()
    goals_against = serializers.IntegerField()
    result = serializers.ChoiceField(
        choices=[(result.value, result.value) for result in TeamMatchResult]
    )


class TeamNextMatchResponse(serializers.Serializer):
    match_id = serializers.UUIDField()
    opponent_name = serializers.CharField()
    scheduled_at = serializers.DateTimeField()


class ListTeamsResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    last_match = TeamLastMatchResponse(allow_null=True)
    next_match = TeamNextMatchResponse(allow_null=True)
