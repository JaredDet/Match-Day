from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE
from modules.matches.domain.shot import ShotOutcome


class RegisterShotRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    goalkeeper_id = serializers.UUIDField(required=False, allow_null=True)
    outcome = EnumChoiceField(ShotOutcome)
    minute = serializers.IntegerField(
        min_value=MIN_MATCH_MINUTE,
        max_value=MAX_MATCH_MINUTE,
    )
    added_minute = serializers.IntegerField(min_value=0, required=False, default=0)

    def validate(self, attrs):
        has_goalkeeper = attrs.get("goalkeeper_id") is not None
        if (attrs["outcome"] == ShotOutcome.SAVED) != has_goalkeeper:
            raise serializers.ValidationError("Solo un tiro atajado debe incluir goalkeeper_id")
        return attrs
