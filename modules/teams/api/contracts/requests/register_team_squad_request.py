from rest_framework import serializers


class SquadPlayerRequest(serializers.Serializer):
    name = serializers.CharField(max_length=200)


class RegisterTeamSquadRequest(serializers.Serializer):
    players = SquadPlayerRequest(many=True, allow_empty=False, max_length=50)
