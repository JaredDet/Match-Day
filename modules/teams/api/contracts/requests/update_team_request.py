from rest_framework import serializers

from core.constants import NAME_MAX_LENGTH


class UpdateTeamRequest(serializers.Serializer):
    name = serializers.CharField(max_length=NAME_MAX_LENGTH, required=False)
    head_coach_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Debe indicar al menos un campo para actualizar")

        return attrs
