from rest_framework import serializers

from core.constants import NAME_MAX_LENGTH


class CreateNewsRequest(serializers.Serializer):
    title = serializers.CharField(max_length=NAME_MAX_LENGTH)
    team_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    cover_image = serializers.ImageField(required=False, allow_null=True)
    content = serializers.JSONField()
