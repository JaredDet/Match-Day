from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.match_event import MatchPeriod


class StartMatchPeriodRequest(serializers.Serializer):
    period = EnumChoiceField(MatchPeriod)
