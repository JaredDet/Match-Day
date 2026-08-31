from rest_framework import serializers

from modules.matches.application.queries.get_match_query import MatchEventType
from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.match_squad_player import MatchSquadRole


class MatchEventResponse(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=[(event.value, event.value) for event in MatchEventType])
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
    player_id = serializers.UUIDField()
    player_name = serializers.CharField()
    minute = serializers.IntegerField()


class MatchSquadPlayerResponse(serializers.Serializer):
    player_id = serializers.UUIDField()
    player_name = serializers.CharField()
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
    shirt_number = serializers.IntegerField()
    role = serializers.ChoiceField(choices=MatchSquadRole.choices)
    is_captain = serializers.BooleanField()


class TeamDetailResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    goals = serializers.IntegerField()
    formation = serializers.ChoiceField(
        choices=MatchFormation.choices,
        allow_null=True,
    )


class MatchTeamDetailResponse(TeamDetailResponse):
    lineup = MatchSquadPlayerResponse(many=True)


class GetMatchResponse(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=MatchStatus.choices)
    scheduled_at = serializers.DateTimeField()
    started_at = serializers.DateTimeField(allow_null=True)
    finished_at = serializers.DateTimeField(allow_null=True)
    stadium_name = serializers.CharField(allow_null=True)
    referee_name = serializers.CharField(allow_null=True)
    home_team = MatchTeamDetailResponse()
    away_team = MatchTeamDetailResponse()
    events = MatchEventResponse(many=True)
