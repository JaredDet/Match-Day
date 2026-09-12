from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.matches.api.contracts.requests.advance_match_period_request import (
    AdvanceMatchPeriodRequest,
)
from modules.matches.api.contracts.requests.create_match_request import CreateMatchRequest
from modules.matches.api.contracts.requests.list_matches_request import ListMatchesRequest
from modules.matches.api.contracts.requests.reduce_penalty_shootout_participants_request import (
    ReducePenaltyShootoutParticipantsRequest,
)
from modules.matches.api.contracts.requests.register_card_request import RegisterCardRequest
from modules.matches.api.contracts.requests.register_corner_kick_request import (
    RegisterCornerKickRequest,
)
from modules.matches.api.contracts.requests.register_foul_request import RegisterFoulRequest
from modules.matches.api.contracts.requests.register_goal_request import RegisterGoalRequest
from modules.matches.api.contracts.requests.register_injury_request import RegisterInjuryRequest
from modules.matches.api.contracts.requests.register_offside_request import RegisterOffsideRequest
from modules.matches.api.contracts.requests.register_penalty_attempt_request import (
    RegisterPenaltyAttemptRequest,
)
from modules.matches.api.contracts.requests.register_penalty_shootout_kick_request import (
    RegisterPenaltyShootoutKickRequest,
)
from modules.matches.api.contracts.requests.register_shot_request import RegisterShotRequest
from modules.matches.api.contracts.requests.register_substitution_request import (
    RegisterSubstitutionRequest,
)
from modules.matches.api.contracts.requests.register_var_review_request import (
    RegisterVarReviewRequest,
)
from modules.matches.api.contracts.requests.set_match_lineup_request import SetMatchLineupRequest
from modules.matches.api.contracts.requests.start_penalty_shootout_request import (
    StartPenaltyShootoutRequest,
)
from modules.matches.api.contracts.requests.update_match_clock_request import (
    UpdateMatchClockRequest,
)
from modules.matches.api.contracts.requests.update_match_details_request import (
    UpdateMatchDetailsRequest,
)
from modules.matches.api.contracts.requests.update_match_possession_request import (
    UpdateMatchPossessionRequest,
)
from modules.matches.api.contracts.responses.get_match_response import GetMatchResponse
from modules.matches.api.contracts.responses.list_matches_response import ListMatchesResponse
from modules.matches.application.commands.advance_match_period_use_case import (
    AdvanceMatchPeriodUseCase,
)
from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.application.commands.disallow_goal_use_case import DisallowGoalUseCase
from modules.matches.application.commands.finish_match_use_case import FinishMatchUseCase
from modules.matches.application.commands.finish_penalty_shootout_use_case import (
    FinishPenaltyShootoutUseCase,
)
from modules.matches.application.commands.reduce_penalty_shootout_participants_use_case import (
    ReducePenaltyShootoutParticipantsUseCase,
)
from modules.matches.application.commands.register_card_use_case import RegisterCardUseCase
from modules.matches.application.commands.register_corner_kick_use_case import (
    RegisterCornerKickUseCase,
)
from modules.matches.application.commands.register_foul_use_case import RegisterFoulUseCase
from modules.matches.application.commands.register_goal_use_case import RegisterGoalUseCase
from modules.matches.application.commands.register_injury_use_case import RegisterInjuryUseCase
from modules.matches.application.commands.register_offside_use_case import RegisterOffsideUseCase
from modules.matches.application.commands.register_penalty_attempt_use_case import (
    RegisterPenaltyAttemptUseCase,
)
from modules.matches.application.commands.register_penalty_shootout_kick_use_case import (
    RegisterPenaltyShootoutKickUseCase,
)
from modules.matches.application.commands.register_shot_use_case import RegisterShotUseCase
from modules.matches.application.commands.register_substitution_use_case import (
    RegisterSubstitutionUseCase,
)
from modules.matches.application.commands.register_var_review_use_case import (
    RegisterVarReviewUseCase,
)
from modules.matches.application.commands.rescind_card_use_case import RescindCardUseCase
from modules.matches.application.commands.set_match_lineup_use_case import (
    LineupPlayerInput,
    SetMatchLineupUseCase,
)
from modules.matches.application.commands.start_match_use_case import StartMatchUseCase
from modules.matches.application.commands.start_penalty_shootout_use_case import (
    StartPenaltyShootoutUseCase,
)
from modules.matches.application.commands.update_match_clock_use_case import (
    UpdateMatchClockUseCase,
)
from modules.matches.application.commands.update_match_details_use_case import (
    UpdateMatchDetailsUseCase,
)
from modules.matches.application.commands.update_match_possession_use_case import (
    UpdateMatchPossessionUseCase,
)
from modules.matches.application.queries.get_match_query import GetMatchQuery
from modules.matches.application.queries.list_matches_query import ListMatchesQuery
from modules.matches.domain.match_event import TeamSide
from modules.matches.errors import MatchErrors


class MatchViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="matches_create",
        request=CreateMatchRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateMatchResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    def create(self, request):
        request_contract = CreateMatchRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateMatchUseCase)
        match_id = use_case.execute(**request_contract.validated_data)

        return Response({"id": str(match_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_list",
        parameters=[ListMatchesRequest],
        responses={status.HTTP_200_OK: ListMatchesResponse(many=True)},
    )
    def list(self, request):
        request_contract = ListMatchesRequest(data=request.query_params)
        request_contract.is_valid(raise_exception=True)

        query = injector_instance.get(ListMatchesQuery)
        matches = query.execute(**request_contract.validated_data)
        return Response(ListMatchesResponse(matches, many=True).data)

    @extend_schema(
        operation_id="matches_retrieve",
        responses={status.HTTP_200_OK: GetMatchResponse},
    )
    def retrieve(self, request, pk=None):
        query = injector_instance.get(GetMatchQuery)
        match = query.execute(pk)
        return Response(GetMatchResponse(match).data)

    @extend_schema(
        operation_id="matches_update_details",
        request=UpdateMatchDetailsRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["patch"], url_path="details")
    def update_details(self, request, pk=None):
        request_contract = UpdateMatchDetailsRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(UpdateMatchDetailsUseCase)
        use_case.execute(match_id=pk, **request_contract.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_set_lineup",
        request=SetMatchLineupRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(
        detail=True,
        methods=["put"],
        url_path="lineups/<str:team_side>",
    )
    def set_lineup(self, request, pk=None, team_side=None):
        request_contract = SetMatchLineupRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        try:
            resolved_team_side = TeamSide(team_side)
        except ValueError:
            raise MatchErrors.InvalidTeamSide from None

        use_case = injector_instance.get(SetMatchLineupUseCase)
        use_case.execute(
            match_id=pk,
            team_side=resolved_team_side,
            formation=request_contract.validated_data["formation"],
            captain_id=request_contract.validated_data.get("captain_id"),
            players=[
                LineupPlayerInput(**player) for player in request_contract.validated_data["players"]
            ],
            substitutes=[
                LineupPlayerInput(**player)
                for player in request_contract.validated_data.get("substitutes", [])
            ],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_start",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        use_case = injector_instance.get(StartMatchUseCase)
        use_case.execute(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_advance_period",
        request=AdvanceMatchPeriodRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["post"], url_path="advance-period")
    def advance_period(self, request, pk=None):
        request_contract = AdvanceMatchPeriodRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(AdvanceMatchPeriodUseCase)
        use_case.execute(match_id=pk, **request_contract.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_update_clock",
        request=UpdateMatchClockRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["patch"], url_path="clock")
    def update_clock(self, request, pk=None):
        request_contract = UpdateMatchClockRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(UpdateMatchClockUseCase)
        use_case.execute(match_id=pk, **request_contract.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_update_possession",
        request=UpdateMatchPossessionRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["patch"], url_path="possession")
    def update_possession(self, request, pk=None):
        request_contract = UpdateMatchPossessionRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(UpdateMatchPossessionUseCase)
        use_case.execute(match_id=pk, **request_contract.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_finish",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["post"], url_path="finish")
    def finish(self, request, pk=None):
        use_case = injector_instance.get(FinishMatchUseCase)
        use_case.execute(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_register_goal",
        request=RegisterGoalRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterGoalResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="goals")
    def register_goal(self, request, pk=None):
        request_contract = RegisterGoalRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterGoalUseCase)
        goal_id = use_case.execute(match_id=pk, **request_contract.validated_data)

        return Response({"id": str(goal_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_register_penalty_attempt",
        request=RegisterPenaltyAttemptRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterPenaltyAttemptResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="penalty-attempts")
    def register_penalty_attempt(self, request, pk=None):
        request_contract = RegisterPenaltyAttemptRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterPenaltyAttemptUseCase)
        penalty_attempt_id = use_case.execute(
            match_id=pk,
            **request_contract.validated_data,
        )

        return Response(
            {"id": str(penalty_attempt_id)},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        operation_id="matches_register_injury",
        request=RegisterInjuryRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterInjuryResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="injuries")
    def register_injury(self, request, pk=None):
        request_contract = RegisterInjuryRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterInjuryUseCase)
        injury_id = use_case.execute(match_id=pk, **request_contract.validated_data)

        return Response({"id": str(injury_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_register_foul",
        request=RegisterFoulRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterFoulResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="fouls")
    def register_foul(self, request, pk=None):
        request_contract = RegisterFoulRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterFoulUseCase)
        event_id = use_case.execute(match_id=pk, **request_contract.validated_data)
        return Response({"id": str(event_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_register_corner_kick",
        request=RegisterCornerKickRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterCornerKickResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="corners")
    def register_corner_kick(self, request, pk=None):
        request_contract = RegisterCornerKickRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterCornerKickUseCase)
        event_id = use_case.execute(match_id=pk, **request_contract.validated_data)
        return Response({"id": str(event_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_register_offside",
        request=RegisterOffsideRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterOffsideResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="offsides")
    def register_offside(self, request, pk=None):
        request_contract = RegisterOffsideRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterOffsideUseCase)
        event_id = use_case.execute(match_id=pk, **request_contract.validated_data)
        return Response({"id": str(event_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_register_shot",
        request=RegisterShotRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterShotResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="shots")
    def register_shot(self, request, pk=None):
        request_contract = RegisterShotRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterShotUseCase)
        event_id = use_case.execute(match_id=pk, **request_contract.validated_data)
        return Response({"id": str(event_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_register_var_review",
        request=RegisterVarReviewRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterVarReviewResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="var-reviews")
    def register_var_review(self, request, pk=None):
        request_contract = RegisterVarReviewRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterVarReviewUseCase)
        var_review_id = use_case.execute(match_id=pk, **request_contract.validated_data)

        return Response({"id": str(var_review_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_register_card",
        request=RegisterCardRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterCardResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="cards")
    def register_card(self, request, pk=None):
        request_contract = RegisterCardRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterCardUseCase)
        card_id = use_case.execute(match_id=pk, **request_contract.validated_data)

        return Response({"id": str(card_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_register_substitution",
        request=RegisterSubstitutionRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterSubstitutionResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="substitutions")
    def register_substitution(self, request, pk=None):
        request_contract = RegisterSubstitutionRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterSubstitutionUseCase)
        substitution_id = use_case.execute(
            match_id=pk,
            **request_contract.validated_data,
        )
        return Response(
            {"id": str(substitution_id)},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        operation_id="matches_start_penalty_shootout",
        request=StartPenaltyShootoutRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="StartPenaltyShootoutResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="penalty-shootout/start")
    def start_penalty_shootout(self, request, pk=None):
        request_contract = StartPenaltyShootoutRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(StartPenaltyShootoutUseCase)
        shootout_id = use_case.execute(
            match_id=pk,
            **request_contract.validated_data,
        )

        return Response({"id": str(shootout_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_register_penalty_shootout_kick",
        request=RegisterPenaltyShootoutKickRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterPenaltyShootoutKickResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="penalty-shootout/kicks")
    def register_penalty_shootout_kick(self, request, pk=None):
        request_contract = RegisterPenaltyShootoutKickRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterPenaltyShootoutKickUseCase)
        kick_id = use_case.execute(match_id=pk, **request_contract.validated_data)

        return Response({"id": str(kick_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="matches_reduce_penalty_shootout_participants",
        request=ReducePenaltyShootoutParticipantsRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="penalty-shootout/participants/reduce",
    )
    def reduce_penalty_shootout_participants(self, request, pk=None):
        request_contract = ReducePenaltyShootoutParticipantsRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(ReducePenaltyShootoutParticipantsUseCase)
        use_case.execute(match_id=pk, **request_contract.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_finish_penalty_shootout",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["post"], url_path="penalty-shootout/finish")
    def finish_penalty_shootout(self, request, pk=None):
        use_case = injector_instance.get(FinishPenaltyShootoutUseCase)
        use_case.execute(match_id=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_disallow_goal",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="goals/<uuid:goal_id>/disallow",
    )
    def disallow_goal(self, request, pk=None, goal_id=None):
        use_case = injector_instance.get(DisallowGoalUseCase)
        use_case.execute(match_id=pk, goal_id=goal_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="matches_rescind_card",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="cards/<uuid:card_id>/rescind",
    )
    def rescind_card(self, request, pk=None, card_id=None):
        use_case = injector_instance.get(RescindCardUseCase)
        use_case.execute(match_id=pk, card_id=card_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
