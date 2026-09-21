from rest_framework import serializers

from modules.recommendations.constants import MAX_ACTIVE_SECONDS_PER_VISIT
from modules.recommendations.domain.content_reference import ContentKind


class RecordActiveTimeRequest(serializers.Serializer):
    navigation_id = serializers.UUIDField()
    content_kind = serializers.ChoiceField(choices=ContentKind.choices)
    content_id = serializers.UUIDField()
    active_seconds = serializers.IntegerField(min_value=0, max_value=MAX_ACTIVE_SECONDS_PER_VISIT)
