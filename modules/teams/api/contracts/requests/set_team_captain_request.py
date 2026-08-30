from rest_framework import serializers


class SetTeamCaptainRequest(serializers.Serializer):
    player_id = serializers.UUIDField()
