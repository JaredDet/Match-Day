from datetime import date

from rest_framework import serializers

from core.constants import NAME_MAX_LENGTH


class UpdateTeamRequest(serializers.Serializer):
    name = serializers.CharField(max_length=NAME_MAX_LENGTH, required=False)
    head_coach_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
    )
    crest = serializers.ImageField(required=False, allow_null=True)
    city = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    stadium_name = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    founded_year = serializers.IntegerField(
        min_value=1800,
        max_value=date.today().year,
        required=False,
        allow_null=True,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Debe indicar al menos un campo para actualizar")

        return attrs
