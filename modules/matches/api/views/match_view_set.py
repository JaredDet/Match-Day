from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.matches.api.contracts.requests.create_match_request import CreateMatchRequest
from modules.matches.api.contracts.requests.list_matches_request import ListMatchesRequest
from modules.matches.api.contracts.requests.register_card_request import RegisterCardRequest
from modules.matches.api.contracts.requests.register_goal_request import RegisterGoalRequest
from modules.matches.api.contracts.requests.update_match_details_request import (
    UpdateMatchDetailsRequest,
)
from modules.matches.api.contracts.responses.get_match_response import GetMatchResponse
from modules.matches.api.contracts.responses.list_matches_response import ListMatchesResponse
from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.application.commands.disallow_goal_use_case import DisallowGoalUseCase
from modules.matches.application.commands.finish_match_use_case import FinishMatchUseCase
from modules.matches.application.commands.register_card_use_case import RegisterCardUseCase
from modules.matches.application.commands.register_goal_use_case import RegisterGoalUseCase
from modules.matches.application.commands.rescind_card_use_case import RescindCardUseCase
from modules.matches.application.commands.start_match_use_case import StartMatchUseCase
from modules.matches.application.commands.update_match_details_use_case import (
    UpdateMatchDetailsUseCase,
)
from modules.matches.application.queries.get_match_query import GetMatchQuery
from modules.matches.application.queries.list_matches_query import ListMatchesQuery


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
