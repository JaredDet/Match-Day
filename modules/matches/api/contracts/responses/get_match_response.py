from rest_framework import serializers

from modules.matches.application.queries.get_match_query import MatchEventType
from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.match_squad_player import MatchSquadRole


class MatchEventResponse(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=[(event.value, event.value) for event in MatchEventType])
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
    minute = serializers.IntegerField()
    period = serializers.ChoiceField(choices=MatchPeriod.choices)
    added_minute = serializers.IntegerField()
    player_id = serializers.UUIDField(allow_null=True)
    player_name = serializers.CharField(allow_null=True)
    player_out_id = serializers.UUIDField(allow_null=True)
    player_out_name = serializers.CharField(allow_null=True)
    player_in_id = serializers.UUIDField(allow_null=True)
    player_in_name = serializers.CharField(allow_null=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {key: value for key, value in representation.items() if value is not None}


class MatchSquadPlayerResponse(serializers.Serializer):
    player_id = serializers.UUIDField()
    player_name = serializers.CharField()
    shirt_number = serializers.IntegerField()
    role = serializers.ChoiceField(choices=MatchSquadRole.choices)
    is_on_field = serializers.BooleanField()
    is_captain = serializers.BooleanField()


class TeamDetailResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
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
    current_period = serializers.ChoiceField(
        choices=MatchPeriod.choices,
        allow_null=True,
    )
    current_minute = serializers.IntegerField(allow_null=True)
    current_added_minute = serializers.IntegerField()
    scheduled_at = serializers.DateTimeField()
    started_at = serializers.DateTimeField(allow_null=True)
    finished_at = serializers.DateTimeField(allow_null=True)
    stadium_name = serializers.CharField(allow_null=True)
    referee_name = serializers.CharField(allow_null=True)
    home_team = MatchTeamDetailResponse()
    away_team = MatchTeamDetailResponse()
    events = MatchEventResponse(many=True)
