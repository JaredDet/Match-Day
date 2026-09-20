from rest_framework import serializers


class ListPhasesRequest(serializers.Serializer):
    season = serializers.UUIDField(source="season_id", required=False)
