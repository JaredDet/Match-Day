from rest_framework import serializers


class ListGroupEntriesResponse(serializers.Serializer):
    id = serializers.UUIDField()
    group = serializers.UUIDField(source="group_id")
    team = serializers.UUIDField(source="team_id")
