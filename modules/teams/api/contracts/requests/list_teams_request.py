from rest_framework import serializers

from core.constants import NAME_MAX_LENGTH


class ListTeamsRequest(serializers.Serializer):
    search = serializers.CharField(
        max_length=NAME_MAX_LENGTH,
        required=False,
        allow_blank=True,
        default=None,
    )
