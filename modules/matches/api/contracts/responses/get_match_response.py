from rest_framework import serializers

from modules.matches.application.queries.get_match_query import MatchEventType
from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.match_squad_player import MatchSquadRole, SentOffReason
from modules.matches.domain.penalty_shootout import (
    PenaltyKickOutcome,
    PenaltyShootoutStatus,
)


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
    goal_type = serializers.CharField(allow_null=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {key: value for key, value in representation.items() if value is not None}


class MatchSquadPlayerResponse(serializers.Serializer):
    player_id = serializers.UUIDField()
    player_name = serializers.CharField()
    shirt_number = serializers.IntegerField()
    role = serializers.ChoiceField(choices=MatchSquadRole.choices)
    is_on_field = serializers.BooleanField()
    is_sent_off = serializers.BooleanField()
    sent_off_reason = serializers.ChoiceField(
        choices=SentOffReason.choices,
        allow_null=True,
    )
    is_captain = serializers.BooleanField()


class PenaltyShootoutKickResponse(serializers.Serializer):
    id = serializers.UUIDField()
    player_id = serializers.UUIDField()
    player_name = serializers.CharField()
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
    sequence_number = serializers.IntegerField()
    outcome = serializers.ChoiceField(choices=PenaltyKickOutcome.choices)


class PenaltyShootoutResponse(serializers.Serializer):
    status = serializers.ChoiceField(choices=PenaltyShootoutStatus.choices)
    home_score = serializers.IntegerField()
    away_score = serializers.IntegerField()
    winner_team_side = serializers.ChoiceField(choices=TeamSide.choices, allow_null=True)
    kicks = PenaltyShootoutKickResponse(many=True)


class TeamDetailResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
    goals = serializers.IntegerField()
    penalty_score = serializers.IntegerField(allow_null=True)
    formation = serializers.ChoiceField(
        choices=MatchFormation.choices,
        allow_null=True,
    )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation["penalty_score"] is None:
            representation.pop("penalty_score")

        return representation


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
    penalty_shootout = PenaltyShootoutResponse(allow_null=True)
