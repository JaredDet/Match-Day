from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.news.domain.news import NewsStatus


class ListNewsRequest(serializers.Serializer):
    status = EnumChoiceField(
        NewsStatus,
        required=False,
        default=None,
    )
    team_id = serializers.UUIDField(
        required=False,
        default=None,
    )
    published_from = serializers.DateTimeField(
        input_formats=["iso-8601"],
        required=False,
        default=None,
    )
    published_to = serializers.DateTimeField(
        input_formats=["iso-8601"],
        required=False,
        default=None,
    )
