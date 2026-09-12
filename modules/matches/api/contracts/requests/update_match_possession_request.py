from rest_framework import serializers


class UpdateMatchPossessionRequest(serializers.Serializer):
    home_percentage = serializers.IntegerField(min_value=0, max_value=100)
