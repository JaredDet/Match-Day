from rest_framework import serializers


class CreateGroupEntryRequest(serializers.Serializer):
    group = serializers.UUIDField(source="group_id")
    team = serializers.UUIDField(source="team_id")
