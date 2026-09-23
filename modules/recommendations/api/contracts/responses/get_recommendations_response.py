from rest_framework import serializers

from core.media_url_field import MediaUrlField
from modules.recommendations.domain.content_reference import ContentKind


class RecommendationItemResponse(serializers.Serializer):
    kind = serializers.ChoiceField(choices=ContentKind.choices)
    id = serializers.UUIDField()
    title = serializers.CharField()
    endpoint = serializers.CharField()
    preview = serializers.CharField(allow_blank=True)
    image = MediaUrlField(allow_null=True)
    score = serializers.FloatField()
    reason = serializers.ChoiceField(
        choices=[
            "similar_visitors",
            "team_interest",
            "tournament_interest",
            "recent_content",
            "live_match",
            "discovery",
        ]
    )


class GetRecommendationsResponse(serializers.Serializer):
    personalized = serializers.BooleanField()
    generated_at = serializers.DateTimeField(allow_null=True)
    expires_at = serializers.DateTimeField(allow_null=True)
    news = RecommendationItemResponse(many=True)
    matches = RecommendationItemResponse(many=True)
    tournaments = RecommendationItemResponse(many=True)
    discovery = RecommendationItemResponse(many=True)
