from rest_framework import serializers


class StandingRowResponse(serializers.Serializer):
    id = serializers.UUIDField()
    w = serializers.IntegerField(source="wins")
    d = serializers.IntegerField(source="draws")
    l = serializers.IntegerField(source="losses")  # noqa: E741 - frontend contract
    gf = serializers.IntegerField(source="goals_for")
    ga = serializers.IntegerField(source="goals_against")
    played = serializers.IntegerField()
    goal_difference = serializers.IntegerField()
    points = serializers.IntegerField()
    qualified = serializers.BooleanField()
    tie_break_required = serializers.BooleanField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not representation["tie_break_required"]:
            representation.pop("tie_break_required")

        return representation


class GetSeasonStandingsResponse(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    phase = serializers.UUIDField(source="phase_id")
    status = serializers.CharField()
    matchdays = serializers.IntegerField()
    rows = StandingRowResponse(many=True)
