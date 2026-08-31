from rest_framework import serializers

from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE


class RegisterGoalRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    minute = serializers.IntegerField(
        min_value=MIN_MATCH_MINUTE,
        max_value=MAX_MATCH_MINUTE,
    )
