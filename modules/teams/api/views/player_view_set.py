from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.teams.api.contracts.requests.list_players_request import ListPlayersRequest
from modules.teams.api.contracts.responses.list_players_response import ListPlayersResponse
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
