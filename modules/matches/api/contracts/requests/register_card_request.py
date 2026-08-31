from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE
from modules.matches.domain.card import CardType


class RegisterCardRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    card_type = EnumChoiceField(CardType)
    minute = serializers.IntegerField(
        min_value=MIN_MATCH_MINUTE,
        max_value=MAX_MATCH_MINUTE,
    )
