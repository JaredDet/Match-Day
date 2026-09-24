from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.match import MatchFormation


class TacticalPositionRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    position_x = serializers.IntegerField(min_value=0, max_value=100)
    position_y = serializers.IntegerField(min_value=0, max_value=100)


class ChangeTacticalFormationRequest(serializers.Serializer):
    formation = EnumChoiceField(MatchFormation)
    positions = TacticalPositionRequest(many=True, min_length=1, max_length=11)
