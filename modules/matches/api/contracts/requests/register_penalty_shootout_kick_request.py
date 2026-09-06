from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.penalty_shootout import PenaltyKickOutcome


class RegisterPenaltyShootoutKickRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    outcome = EnumChoiceField(PenaltyKickOutcome)
