from rest_framework import serializers


class ListSeasonsRequest(serializers.Serializer):
    tournament = serializers.UUIDField(source="tournament_id", required=False)
