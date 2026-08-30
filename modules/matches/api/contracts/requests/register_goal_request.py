from rest_framework import serializers


class RegisterGoalRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
    minute = serializers.IntegerField(min_value=0, max_value=130)
