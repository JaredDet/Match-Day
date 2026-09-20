from rest_framework import serializers


class GenerateBracketRequest(serializers.Serializer):
    starts_at = serializers.DateTimeField()
    team_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, min_length=2, max_length=64
    )
    source_phase_id = serializers.UUIDField(required=False)
    round_interval_days = serializers.IntegerField(min_value=1, max_value=365, default=7)
    third_place = serializers.BooleanField(default=True)

    def validate(self, attrs):
        if ("team_ids" in attrs) == ("source_phase_id" in attrs):
            raise serializers.ValidationError("Indica team_ids o source_phase_id, solo uno.")

        return attrs
