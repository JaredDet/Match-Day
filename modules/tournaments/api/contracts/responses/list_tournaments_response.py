from rest_framework import serializers


class ListTournamentsResponse(serializers.Serializer):
    id = serializers.UUIDField()
    slug = serializers.CharField()
    name = serializers.CharField()
    country = serializers.CharField()
    category = serializers.CharField()
    max_teams_per_group = serializers.IntegerField()
