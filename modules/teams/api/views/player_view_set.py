from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.teams.api.contracts.requests.list_players_request import ListPlayersRequest
from modules.teams.api.contracts.responses.get_player_response import GetPlayerResponse
from modules.teams.api.contracts.responses.list_players_response import ListPlayersResponse
from modules.teams.application.queries.get_player_query import GetPlayerQuery
from modules.teams.application.queries.list_players_query import ListPlayersQuery


class PlayerViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="players_list",
        parameters=[ListPlayersRequest],
        responses={status.HTTP_200_OK: ListPlayersResponse(many=True)},
    )
    def list(self, request):
        request_contract = ListPlayersRequest(data=request.query_params)
        request_contract.is_valid(raise_exception=True)

        query = injector_instance.get(ListPlayersQuery)
        players = query.execute(**request_contract.validated_data)
        return Response(ListPlayersResponse(players, many=True).data)

    @extend_schema(
        operation_id="players_retrieve",
        responses={status.HTTP_200_OK: GetPlayerResponse},
    )
    def retrieve(self, request, pk=None):
        query = injector_instance.get(GetPlayerQuery)
        player = query.execute(pk)
        return Response(GetPlayerResponse(player).data)
