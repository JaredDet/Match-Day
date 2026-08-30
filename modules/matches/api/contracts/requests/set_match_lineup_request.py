from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.match import MatchFormation


class LineupPlayerRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    shirt_number = serializers.IntegerField(min_value=1, max_value=99)


class SetMatchLineupRequest(serializers.Serializer):
    formation = EnumChoiceField(MatchFormation)
    captain_id = serializers.UUIDField(required=False, allow_null=True)
    players = LineupPlayerRequest(many=True, min_length=11, max_length=11)
