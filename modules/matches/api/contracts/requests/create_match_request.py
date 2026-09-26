from rest_framework import serializers

from core.constants import NAME_MAX_LENGTH
from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.match import MatchFormation


class CreateMatchRequest(serializers.Serializer):
    home_team_id = serializers.UUIDField()
    away_team_id = serializers.UUIDField()
    scheduled_at = serializers.DateTimeField(input_formats=["iso-8601"])
    home_formation = EnumChoiceField(MatchFormation, required=False)
    away_formation = EnumChoiceField(MatchFormation, required=False)
    stadium_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    referee_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
