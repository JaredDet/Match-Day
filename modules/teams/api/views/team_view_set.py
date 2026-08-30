from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.teams.api.contracts.requests.create_team_request import CreateTeamRequest
from modules.teams.api.contracts.requests.list_teams_request import ListTeamsRequest
from modules.teams.api.contracts.requests.register_player_request import RegisterPlayerRequest
from modules.teams.api.contracts.requests.register_team_squad_request import (
    RegisterTeamSquadRequest,
)
from modules.teams.api.contracts.requests.update_team_request import UpdateTeamRequest
from modules.teams.api.contracts.responses.get_team_response import GetTeamResponse
from modules.teams.api.contracts.responses.list_teams_response import ListTeamsResponse
from modules.teams.application.commands.create_team_use_case import CreateTeamUseCase
from modules.teams.application.commands.register_player_use_case import RegisterPlayerUseCase
from modules.teams.application.commands.register_team_squad_use_case import (
    RegisterTeamSquadUseCase,
)
from modules.teams.application.commands.update_team_use_case import UpdateTeamUseCase
from modules.teams.application.queries.get_team_query import GetTeamQuery
from modules.teams.application.queries.list_teams_query import ListTeamsQuery


class TeamViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="teams_create",
        request=CreateTeamRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateTeamResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    def create(self, request):
        request_contract = CreateTeamRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateTeamUseCase)
        team_id = use_case.execute(**request_contract.validated_data)
        return Response({"id": str(team_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="teams_list",
        parameters=[ListTeamsRequest],
        responses={status.HTTP_200_OK: ListTeamsResponse(many=True)},
    )
    def list(self, request):
        request_contract = ListTeamsRequest(data=request.query_params)
        request_contract.is_valid(raise_exception=True)

        query = injector_instance.get(ListTeamsQuery)
        teams = query.execute(**request_contract.validated_data)
        return Response(ListTeamsResponse(teams, many=True).data)

    @extend_schema(
        operation_id="teams_retrieve",
        responses={status.HTTP_200_OK: GetTeamResponse},
    )
    def retrieve(self, request, pk=None):
        query = injector_instance.get(GetTeamQuery)
        team = query.execute(pk)
        return Response(GetTeamResponse(team).data)

    @extend_schema(
        operation_id="teams_update",
        request=UpdateTeamRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def partial_update(self, request, pk=None):
        request_contract = UpdateTeamRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(UpdateTeamUseCase)
        use_case.execute(team_id=pk, **request_contract.validated_data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="teams_register_player",
        request=RegisterPlayerRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterPlayerResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="players")
    def register_player(self, request, pk=None):
        request_contract = RegisterPlayerRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterPlayerUseCase)
        player_id = use_case.execute(team_id=pk, **request_contract.validated_data)
        return Response({"id": str(player_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="teams_register_squad",
        request=RegisterTeamSquadRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="RegisterTeamSquadResult",
                fields={"ids": serializers.ListField(child=serializers.UUIDField())},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="squad")
    def register_squad(self, request, pk=None):
        request_contract = RegisterTeamSquadRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(RegisterTeamSquadUseCase)
        player_ids = use_case.execute(
            team_id=pk,
            player_names=[player["name"] for player in request_contract.validated_data["players"]],
        )
        return Response(
            {"ids": [str(player_id) for player_id in player_ids]},
            status=status.HTTP_201_CREATED,
        )
