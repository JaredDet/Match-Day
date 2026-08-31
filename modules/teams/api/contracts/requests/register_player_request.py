from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.teams.domain.player import PlayerPosition


class RegisterPlayerRequest(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    preferred_position = EnumChoiceField(PlayerPosition, required=False, allow_null=True)
    preferred_shirt_number = serializers.IntegerField(
        min_value=1,
        max_value=99,
        required=False,
        allow_null=True,
    )
