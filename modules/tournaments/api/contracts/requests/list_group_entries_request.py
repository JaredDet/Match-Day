from rest_framework import serializers


class ListGroupEntriesRequest(serializers.Serializer):
    group = serializers.UUIDField(source="group_id", required=False)
