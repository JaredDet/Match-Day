from rest_framework import serializers

from core.constants import NAME_MAX_LENGTH


class UpdateMatchDetailsRequest(serializers.Serializer):
    stadium_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    referee_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Debe enviar al menos un detalle")
        return attrs
