from rest_framework import serializers

from modules.tournaments.domain.phase import PhaseKind, PhaseStatus


class ListPhasesResponse(serializers.Serializer):
    id = serializers.UUIDField()
    season = serializers.UUIDField(source="season_id")
    name = serializers.CharField()
    kind = serializers.ChoiceField(choices=PhaseKind.choices)
    order = serializers.IntegerField()
    status = serializers.ChoiceField(choices=PhaseStatus.choices)
    qualifying_teams = serializers.IntegerField()
    matchdays = serializers.IntegerField()
    generated = serializers.BooleanField()
    source_phase = serializers.UUIDField(source="source_phase_id", allow_null=True)
    scheduled_at = serializers.DateTimeField(allow_null=True)
    expected_matches = serializers.IntegerField(allow_null=True)
