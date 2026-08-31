from rest_framework import serializers

from core.constants import NAME_MAX_LENGTH


class UpdateTeamRequest(serializers.Serializer):
    name = serializers.CharField(max_length=NAME_MAX_LENGTH)
