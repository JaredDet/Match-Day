from rest_framework import serializers

from modules.tournaments.constants import DEFAULT_MAX_TEAMS_PER_GROUP


class CreateTournamentRequest(serializers.Serializer):
    slug = serializers.SlugField(max_length=50)
    name = serializers.CharField(max_length=150)
    country = serializers.CharField(max_length=100)
    category = serializers.CharField(max_length=100)
    logo = serializers.ImageField(required=False, allow_null=True)
    max_teams_per_group = serializers.IntegerField(
        min_value=1, max_value=32767, default=DEFAULT_MAX_TEAMS_PER_GROUP
    )
