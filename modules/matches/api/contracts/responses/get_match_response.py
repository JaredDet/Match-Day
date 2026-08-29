from rest_framework import serializers

from modules.matches.application.queries.get_match_query import MatchEventType
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import TeamSide


class TeamDetailResponse(serializers.Serializer):
    name = serializers.CharField()
    goals = serializers.IntegerField()


class MatchEventResponse(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=[(event.value, event.value) for event in MatchEventType])
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
    player_name = serializers.CharField()
    minute = serializers.IntegerField()


class GetMatchResponse(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=MatchStatus.choices)
    scheduled_at = serializers.DateTimeField()
    started_at = serializers.DateTimeField(allow_null=True)
    finished_at = serializers.DateTimeField(allow_null=True)
    home_team = TeamDetailResponse()
    away_team = TeamDetailResponse()
    events = MatchEventResponse(many=True)
