from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.card import CardType


class RegisterCardRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    card_type = EnumChoiceField(CardType)
    minute = serializers.IntegerField(min_value=0, max_value=130)
