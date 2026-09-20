from rest_framework import serializers


class CupTieResponse(serializers.Serializer):
    id = serializers.UUIDField()
    home = serializers.UUIDField(source="home_id")
    away = serializers.UUIDField(source="away_id")
    homeScore = serializers.IntegerField(source="home_score", allow_null=True)  # noqa: N815
    awayScore = serializers.IntegerField(source="away_score", allow_null=True)  # noqa: N815
    penalties = serializers.ListField(child=serializers.IntegerField(), allow_null=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation["penalties"] is None:
            representation.pop("penalties")

        return representation


class BracketRoundResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    ties = CupTieResponse(many=True)


class GetSeasonBracketResponse(serializers.Serializer):
    rounds = BracketRoundResponse(many=True)
    third = CupTieResponse(allow_null=True)
