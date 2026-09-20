from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.tournaments.domain.phase import PhaseStatus


class SetPhaseStatusRequest(serializers.Serializer):
    status = EnumChoiceField(PhaseStatus)
