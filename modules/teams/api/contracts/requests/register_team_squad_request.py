from rest_framework import serializers

from core.constants import MAX_SHIRT_NUMBER, MIN_SHIRT_NUMBER, NAME_MAX_LENGTH
from core.enum_choice_field import EnumChoiceField
from modules.teams.domain.player import PlayerPosition

MAX_SQUAD_SIZE = 50


class SquadPlayerRequest(serializers.Serializer):
    name = serializers.CharField(max_length=NAME_MAX_LENGTH)
    preferred_position = EnumChoiceField(PlayerPosition, required=False, allow_null=True)
    preferred_shirt_number = serializers.IntegerField(
        min_value=MIN_SHIRT_NUMBER,
        max_value=MAX_SHIRT_NUMBER,
        required=False,
        allow_null=True,
    )


class RegisterTeamSquadRequest(serializers.Serializer):
    players = SquadPlayerRequest(
        many=True,
        allow_empty=False,
        max_length=MAX_SQUAD_SIZE,
    )
