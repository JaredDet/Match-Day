from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.recommendations.api.schema import NAVIGATION_PARAMETERS
from modules.tournaments.api.contracts.requests.create_tournament_request import (
    CreateTournamentRequest,
)
from modules.tournaments.api.contracts.responses.get_tournament_response import (
    GetTournamentResponse,
)
from modules.tournaments.api.contracts.responses.list_seasons_response import ListSeasonsResponse
from modules.tournaments.api.contracts.responses.list_tournaments_response import (
    ListTournamentsResponse,
)
from modules.tournaments.application.commands.create_tournament_use_case import (
    CreateTournamentUseCase,
)
from modules.tournaments.application.queries.get_tournament_query import GetTournamentQuery
from modules.tournaments.application.queries.list_seasons_query import ListSeasonsQuery
from modules.tournaments.application.queries.list_tournaments_query import ListTournamentsQuery


class TournamentViewSet(ViewSet):
    lookup_value_converter = "slug"
    lookup_field = "slug"

    @extend_schema(
        operation_id="tournaments_create",
        request=CreateTournamentRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateTournamentResult", fields={"id": serializers.UUIDField()}
            )
        },
    )
    def create(self, request):
        request_contract = CreateTournamentRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateTournamentUseCase)
        entity_id = use_case.execute(**request_contract.validated_data)

        return Response({"id": str(entity_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="tournaments_list",
        responses={status.HTTP_200_OK: ListTournamentsResponse(many=True)},
    )
    def list(self, request):
        query = injector_instance.get(ListTournamentsQuery)
        result = query.execute()

        return Response(
            ListTournamentsResponse(result, many=True, context={"request": request}).data
        )

    @extend_schema(
        operation_id="tournaments_retrieve",
        parameters=NAVIGATION_PARAMETERS,
        responses={status.HTTP_200_OK: GetTournamentResponse},
    )
    def retrieve(self, request, slug=None):
        query = injector_instance.get(GetTournamentQuery)
        result = query.execute(slug)

        return Response(GetTournamentResponse(result, context={"request": request}).data)

    @extend_schema(
        operation_id="tournaments_list_seasons",
        responses={status.HTTP_200_OK: ListSeasonsResponse(many=True)},
    )
    @action(detail=True, methods=["get"])
    def seasons(self, request, slug=None):
        tournament = injector_instance.get(GetTournamentQuery).execute(slug)
        result = injector_instance.get(ListSeasonsQuery).execute(tournament_id=tournament.id)

        return Response(ListSeasonsResponse(result, many=True).data)
