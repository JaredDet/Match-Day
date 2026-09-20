from rest_framework import serializers


class SetGroupTieBreakRequest(serializers.Serializer):
    team_ids = serializers.ListField(child=serializers.UUIDField())
