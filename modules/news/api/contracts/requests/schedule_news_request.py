from rest_framework import serializers


class ScheduleNewsRequest(serializers.Serializer):
    scheduled_at = serializers.DateTimeField()
