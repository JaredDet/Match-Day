from rest_framework import serializers

from core.constants import NAME_MAX_LENGTH, NEWS_PREVIEW_MAX_LENGTH


class UpdateNewsRequest(serializers.Serializer):
    title = serializers.CharField(max_length=NAME_MAX_LENGTH)
    content = serializers.JSONField()
    preview = serializers.CharField(
        max_length=NEWS_PREVIEW_MAX_LENGTH, required=False, allow_blank=True
    )
    cover_image = serializers.ImageField(required=False, allow_null=True)
