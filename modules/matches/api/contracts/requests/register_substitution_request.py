from rest_framework import serializers

from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE


class RegisterSubstitutionRequest(serializers.Serializer):
    player_out_id = serializers.UUIDField()
    player_in_id = serializers.UUIDField()
    minute = serializers.IntegerField(
        min_value=MIN_MATCH_MINUTE,
        max_value=MAX_MATCH_MINUTE,
    )
    added_minute = serializers.IntegerField(min_value=0, required=False, default=0)

    def validate(self, attrs):
        if attrs["player_out_id"] == attrs["player_in_id"]:
            raise serializers.ValidationError(
                "El jugador que sale y el que entra deben ser diferentes"
            )
        return attrs
