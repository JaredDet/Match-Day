from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.tournaments.domain.phase import PhaseKind, PhaseStatus


class CreatePhaseRequest(serializers.Serializer):
    season = serializers.UUIDField(source="season_id")
    name = serializers.CharField(max_length=100)
    kind = EnumChoiceField(PhaseKind)
    order = serializers.IntegerField(min_value=0, max_value=32767)
    status = EnumChoiceField(PhaseStatus, required=False)
    qualifying_teams = serializers.IntegerField(min_value=0, max_value=32767, required=False)
    matchdays = serializers.IntegerField(min_value=1, max_value=32767, required=False)
