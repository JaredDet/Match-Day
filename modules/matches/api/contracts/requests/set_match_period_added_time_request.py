from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.match_event import MatchPeriod


class SetMatchPeriodAddedTimeRequest(serializers.Serializer):
    expected_period = EnumChoiceField(MatchPeriod)
    minutes = serializers.IntegerField(min_value=0)
