from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.tournaments.domain.phase import PhaseKind


class UpdatePhaseRequest(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    kind = EnumChoiceField(PhaseKind, required=False)
    order = serializers.IntegerField(min_value=0, max_value=32767, required=False)
    matchdays = serializers.IntegerField(min_value=1, max_value=32767, required=False)
    qualifying_teams = serializers.IntegerField(min_value=0, max_value=32767, required=False)
