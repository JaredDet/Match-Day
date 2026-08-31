from rest_framework import serializers

from modules.matches.api.contracts.responses.get_match_response import TeamDetailResponse
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import MatchPeriod


class ListMatchesResponse(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=MatchStatus.choices)
    current_period = serializers.ChoiceField(
        choices=MatchPeriod.choices,
        allow_null=True,
    )
    current_minute = serializers.IntegerField(allow_null=True)
    current_added_minute = serializers.IntegerField()
    scheduled_at = serializers.DateTimeField()
    home_team = TeamDetailResponse()
    away_team = TeamDetailResponse()
