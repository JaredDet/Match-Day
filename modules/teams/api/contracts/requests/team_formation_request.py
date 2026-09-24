from rest_framework import serializers

from modules.teams.domain.formation import FORMATION_CHOICES


class FormationPositionRequest(serializers.Serializer):
    slot = serializers.IntegerField(min_value=1, max_value=11)
    x = serializers.IntegerField(min_value=0, max_value=100)
    y = serializers.IntegerField(min_value=0, max_value=100)


class TeamFormationRequest(serializers.Serializer):
    name = serializers.CharField(max_length=80)
    shape = serializers.ChoiceField(choices=FORMATION_CHOICES)
    positions = FormationPositionRequest(many=True, min_length=11, max_length=11)
    is_default = serializers.BooleanField(required=False, default=False)
