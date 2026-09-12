from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE
from modules.matches.domain.penalty_attempt import PenaltyAttemptOutcome


class RegisterPenaltyAttemptRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    outcome = EnumChoiceField(PenaltyAttemptOutcome)
    minute = serializers.IntegerField(
        min_value=MIN_MATCH_MINUTE,
        max_value=MAX_MATCH_MINUTE,
    )
    added_minute = serializers.IntegerField(min_value=0, required=False, default=0)
