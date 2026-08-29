from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.domain.match import MatchStatus


class ListMatchesRequest(serializers.Serializer):
    status = EnumChoiceField(MatchStatus, required=False)
    date = serializers.DateField(input_formats=["iso-8601"], required=False)
