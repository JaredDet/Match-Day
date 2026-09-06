from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE
from modules.matches.domain.goal import GoalType


class RegisterGoalRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    goal_type = EnumChoiceField(GoalType, required=False, default=GoalType.REGULAR)
    minute = serializers.IntegerField(
        min_value=MIN_MATCH_MINUTE,
        max_value=MAX_MATCH_MINUTE,
    )
    added_minute = serializers.IntegerField(min_value=0, required=False, default=0)
