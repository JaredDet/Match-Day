from rest_framework import serializers

from core.constants import NEWS_PREVIEW_MAX_LENGTH
from core.enum_choice_field import EnumChoiceField
from modules.news.domain.news import NewsStatus


class ListNewsResponse(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    team_id = serializers.UUIDField(allow_null=True)
    cover_image = serializers.CharField(allow_null=True)
    preview = serializers.CharField(max_length=NEWS_PREVIEW_MAX_LENGTH, allow_blank=True)
    status = EnumChoiceField(NewsStatus)
    scheduled_at = serializers.DateTimeField(allow_null=True)
    published_at = serializers.DateTimeField(allow_null=True)
