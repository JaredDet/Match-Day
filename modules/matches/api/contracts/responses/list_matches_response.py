from rest_framework import serializers

from modules.matches.api.contracts.responses.get_match_response import MatchClockResponse
from modules.matches.domain.goal import GoalType
from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide


class MatchGoalPreviewResponse(serializers.Serializer):
    player_name = serializers.CharField()
    assist_player_name = serializers.CharField(allow_null=True)
    goal_type = serializers.ChoiceField(choices=GoalType.choices)
    minute = serializers.IntegerField()
    added_minute = serializers.IntegerField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation["added_minute"] == 0:
            representation.pop("added_minute")

        if representation["assist_player_name"] is None:
            representation.pop("assist_player_name")

        return representation


class MatchTeamPreviewResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    team_side = serializers.ChoiceField(choices=TeamSide.choices)
    score = serializers.IntegerField()
    penalty_score = serializers.IntegerField(allow_null=True)
    formation = serializers.ChoiceField(choices=MatchFormation.choices, allow_null=True)
    goals = MatchGoalPreviewResponse(many=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation["penalty_score"] is None:
            representation.pop("penalty_score")

        return representation


class ListMatchesResponse(serializers.Serializer):
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
    home_team = MatchTeamPreviewResponse()
    away_team = MatchTeamPreviewResponse()
