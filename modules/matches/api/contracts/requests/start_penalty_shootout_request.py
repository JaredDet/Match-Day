from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.match_event import TeamSide


class StartPenaltyShootoutRequest(serializers.Serializer):
    starting_team_side = EnumChoiceField(TeamSide)
    equalization_excluded_player_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )
