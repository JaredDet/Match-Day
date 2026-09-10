from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.penalty_shootout import PenaltyShootoutDepartureReason


class ReducePenaltyShootoutParticipantsRequest(serializers.Serializer):
    unavailable_player_id = serializers.UUIDField()
    departure_reason = EnumChoiceField(PenaltyShootoutDepartureReason)
    opponent_excluded_player_id = serializers.UUIDField()
