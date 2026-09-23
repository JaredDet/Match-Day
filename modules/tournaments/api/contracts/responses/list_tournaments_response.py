from rest_framework import serializers

from core.media_url_field import MediaUrlField


class ListTournamentsResponse(serializers.Serializer):
    id = serializers.UUIDField()
    slug = serializers.CharField()
    name = serializers.CharField()
    country = serializers.CharField()
    category = serializers.CharField()
    logo = MediaUrlField(allow_null=True)
    max_teams_per_group = serializers.IntegerField()
