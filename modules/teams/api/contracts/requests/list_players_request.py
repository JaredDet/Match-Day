from rest_framework import serializers


class ListPlayersRequest(serializers.Serializer):
    search = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        default=None,
    )
    team_id = serializers.UUIDField(required=False, allow_null=True, default=None)
