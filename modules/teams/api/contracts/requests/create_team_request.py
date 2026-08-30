from rest_framework import serializers


class CreateTeamRequest(serializers.Serializer):
    name = serializers.CharField(max_length=200)
