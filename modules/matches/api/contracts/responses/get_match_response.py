from rest_framework import serializers

from core.media_url_field import MediaUrlField
from modules.matches.application.queries.get_match_query import MatchEventType
from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_clock import MatchClockStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.match_squad_player import MatchSquadRole, SentOffReason
from modules.matches.domain.match_substitution import SubstitutionReason
from modules.matches.domain.penalty_attempt import PenaltyAttemptOutcome
from modules.matches.domain.penalty_shootout import (
    PenaltyKickOutcome,
    PenaltyShootoutIneligibilityReason,
    PenaltyShootoutStatus,
)
from modules.matches.domain.shot import ShotOutcome
from modules.matches.domain.var_review import VarReviewDecision, VarReviewReason


class MatchEventResponse(serializers.Serializer):
    id = serializers.UUIDField()
    type = serializers.ChoiceField(choices=[(event.value, event.value) for event in MatchEventType])
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
    minute = serializers.IntegerField(allow_null=True)
    period = serializers.ChoiceField(choices=MatchPeriod.choices, allow_null=True)
    added_minute = serializers.IntegerField(allow_null=True)
    player_id = serializers.UUIDField(allow_null=True)
    player_name = serializers.CharField(allow_null=True)
    assist_player_id = serializers.UUIDField(allow_null=True)
    assist_player_name = serializers.CharField(allow_null=True)
    player_out_id = serializers.UUIDField(allow_null=True)
    player_out_name = serializers.CharField(allow_null=True)
    player_in_id = serializers.UUIDField(allow_null=True)
    player_in_name = serializers.CharField(allow_null=True)
    substitution_reason = serializers.ChoiceField(
        choices=SubstitutionReason.choices,
        allow_null=True,
    )
    goal_type = serializers.CharField(allow_null=True)
    penalty_outcome = serializers.ChoiceField(
        choices=PenaltyAttemptOutcome.choices,
        allow_null=True,
    )
    shot_outcome = serializers.ChoiceField(choices=ShotOutcome.choices, allow_null=True)
    goalkeeper_id = serializers.UUIDField(allow_null=True)
    goalkeeper_name = serializers.CharField(allow_null=True)
    var_reason = serializers.ChoiceField(choices=VarReviewReason.choices, allow_null=True)
    var_decision = serializers.ChoiceField(
        choices=VarReviewDecision.choices,
        allow_null=True,
    )
    reviewed_event_id = serializers.UUIDField(allow_null=True)
    sequence_number = serializers.IntegerField(allow_null=True)
    outcome = serializers.ChoiceField(
        choices=PenaltyKickOutcome.choices,
        allow_null=True,
    )

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


class PenaltyShootoutParticipantResponse(serializers.Serializer):
    player_id = serializers.UUIDField()
    player_name = serializers.CharField()
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
    is_eligible = serializers.BooleanField()
    ineligibility_reason = serializers.ChoiceField(
        choices=PenaltyShootoutIneligibilityReason.choices,
        allow_null=True,
    )
    became_ineligible_at = serializers.DateTimeField(allow_null=True)


class PenaltyShootoutResponse(serializers.Serializer):
    status = serializers.ChoiceField(choices=PenaltyShootoutStatus.choices)
    starting_team_side = serializers.ChoiceField(choices=TeamSide.choices)
    next_team_side = serializers.ChoiceField(
        choices=TeamSide.choices,
        allow_null=True,
    )
    home_participant_ids = serializers.ListField(child=serializers.UUIDField())
    away_participant_ids = serializers.ListField(child=serializers.UUIDField())
    home_score = serializers.IntegerField()
    away_score = serializers.IntegerField()
    winner_team_side = serializers.ChoiceField(choices=TeamSide.choices, allow_null=True)
    participants = PenaltyShootoutParticipantResponse(many=True)


class TeamDetailResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    crest = MediaUrlField(allow_null=True)
    head_coach_name = serializers.CharField(allow_null=True)
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
        if representation["head_coach_name"] is None:
            representation.pop("head_coach_name")

        return representation


class MatchTeamStatisticsResponse(serializers.Serializer):
    possession = serializers.IntegerField(allow_null=True)
    yellow_cards = serializers.IntegerField()
    red_cards = serializers.IntegerField()
    shots = serializers.IntegerField()
    shots_on_target = serializers.IntegerField()
    saves = serializers.IntegerField()
    fouls = serializers.IntegerField()
    corners = serializers.IntegerField()
    offsides = serializers.IntegerField()


class MatchTeamDetailResponse(TeamDetailResponse):
    statistics = MatchTeamStatisticsResponse()
    lineup = MatchSquadPlayerResponse(many=True)


class MatchClockResponse(serializers.Serializer):
    period = serializers.ChoiceField(choices=MatchPeriod.choices, allow_null=True)
    status = serializers.ChoiceField(choices=MatchClockStatus.choices)
    minute = serializers.IntegerField(allow_null=True)
    second = serializers.IntegerField()
    added_minute = serializers.IntegerField()
    elapsed_seconds = serializers.IntegerField()
    remaining_seconds = serializers.IntegerField(allow_null=True)
    deadline_at = serializers.DateTimeField(allow_null=True)
    announced_added_minutes = serializers.IntegerField()
    version = serializers.IntegerField()
    as_of = serializers.DateTimeField()


class GetMatchResponse(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=MatchStatus.choices)
    current_period = serializers.ChoiceField(
        choices=MatchPeriod.choices,
        allow_null=True,
    )
    current_minute = serializers.IntegerField(allow_null=True)
    current_added_minute = serializers.IntegerField()
    clock = MatchClockResponse()
    scheduled_at = serializers.DateTimeField()
    started_at = serializers.DateTimeField(allow_null=True)
    finished_at = serializers.DateTimeField(allow_null=True)
    stadium_name = serializers.CharField(allow_null=True)
    referee_name = serializers.CharField(allow_null=True)
    home_team = MatchTeamDetailResponse()
    away_team = MatchTeamDetailResponse()
    events = MatchEventResponse(many=True)
    penalty_shootout = PenaltyShootoutResponse(allow_null=True)
