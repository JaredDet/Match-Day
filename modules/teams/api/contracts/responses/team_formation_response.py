from rest_framework import serializers

from modules.teams.api.contracts.requests.team_formation_request import FormationPositionRequest
from modules.teams.domain.formation import FORMATION_CHOICES


class TeamFormationResponse(serializers.Serializer):
    id = serializers.UUIDField()
    team_id = serializers.UUIDField()
    name = serializers.CharField()
    shape = serializers.ChoiceField(choices=FORMATION_CHOICES)
    positions = FormationPositionRequest(many=True)
    is_default = serializers.BooleanField()
