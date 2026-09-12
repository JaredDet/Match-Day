from rest_framework import serializers

from core.enum_choice_field import EnumChoiceField
from modules.matches.constants import MAX_MATCH_MINUTE, MIN_MATCH_MINUTE
from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.var_review import VarReviewDecision, VarReviewReason


class RegisterVarReviewRequest(serializers.Serializer):
    team_side = EnumChoiceField(TeamSide)
    reason = EnumChoiceField(VarReviewReason)
    decision = EnumChoiceField(VarReviewDecision)
    reviewed_event_id = serializers.UUIDField(required=False, allow_null=True)
    minute = serializers.IntegerField(
        min_value=MIN_MATCH_MINUTE,
        max_value=MAX_MATCH_MINUTE,
    )
    added_minute = serializers.IntegerField(min_value=0, required=False, default=0)
