from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.news.domain.news import NewsStatus


class GetNewsResponse(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    team_id = serializers.UUIDField(allow_null=True)
    cover_image = serializers.CharField(allow_null=True)
    content = serializers.JSONField()
    status = EnumChoiceField(NewsStatus)
    scheduled_at = serializers.DateTimeField(allow_null=True)
    published_at = serializers.DateTimeField(allow_null=True)
