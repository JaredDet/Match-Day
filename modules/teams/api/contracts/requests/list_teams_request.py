from rest_framework import serializers


class ListTeamsRequest(serializers.Serializer):
    search = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        default=None,
    )
