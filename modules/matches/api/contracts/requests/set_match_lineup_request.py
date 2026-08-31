from rest_framework import serializers

from core.constants import MAX_SHIRT_NUMBER, MIN_SHIRT_NUMBER
from core.enum_choice_field import EnumChoiceField
from modules.matches.constants import MATCH_LINEUP_SIZE
from modules.matches.domain.match import MatchFormation


class LineupPlayerRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    shirt_number = serializers.IntegerField(
        min_value=MIN_SHIRT_NUMBER,
        max_value=MAX_SHIRT_NUMBER,
    )


class SetMatchLineupRequest(serializers.Serializer):
    formation = EnumChoiceField(MatchFormation)
    captain_id = serializers.UUIDField(required=False, allow_null=True)
    players = LineupPlayerRequest(
        many=True,
        min_length=MATCH_LINEUP_SIZE,
        max_length=MATCH_LINEUP_SIZE,
    )
    substitutes = LineupPlayerRequest(many=True, required=False, allow_empty=True)
