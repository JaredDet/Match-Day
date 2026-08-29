from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.match_event import TeamSide


class RegisterGoalRequest(serializers.Serializer):
    team_side = EnumChoiceField(TeamSide)
    player_name = serializers.CharField(max_length=200)
    minute = serializers.IntegerField(min_value=0, max_value=130)
