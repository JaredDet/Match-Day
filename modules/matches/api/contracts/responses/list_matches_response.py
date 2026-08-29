from rest_framework import serializers

from modules.matches.api.contracts.responses.get_match_response import TeamDetailResponse
from modules.matches.domain.match import MatchStatus


class ListMatchesResponse(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=MatchStatus.choices)
    scheduled_at = serializers.DateTimeField()
    home_team = TeamDetailResponse()
    away_team = TeamDetailResponse()
