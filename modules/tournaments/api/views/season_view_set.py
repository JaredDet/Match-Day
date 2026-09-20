from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.tournaments.api.contracts.requests.create_season_request import CreateSeasonRequest
from modules.tournaments.api.contracts.requests.generate_bracket_request import (
    GenerateBracketRequest,
)
from modules.tournaments.api.contracts.requests.list_seasons_request import ListSeasonsRequest
from modules.tournaments.api.contracts.requests.season_team_request import SeasonTeamRequest
from modules.tournaments.api.contracts.responses.get_season_bracket_response import (
    GetSeasonBracketResponse,
)
from modules.tournaments.api.contracts.responses.get_season_response import GetSeasonResponse
from modules.tournaments.api.contracts.responses.get_season_standings_response import (
    GetSeasonStandingsResponse,
)
from modules.tournaments.api.contracts.responses.list_fixtures_response import ListFixturesResponse
from modules.tournaments.api.contracts.responses.list_seasons_response import ListSeasonsResponse
from modules.tournaments.application.commands.add_season_team_use_case import AddSeasonTeamUseCase
from modules.tournaments.application.commands.advance_bracket_use_case import AdvanceBracketUseCase
from modules.tournaments.application.commands.create_season_use_case import CreateSeasonUseCase
from modules.tournaments.application.commands.generate_bracket_use_case import (
    GenerateBracketUseCase,
)
from modules.tournaments.application.commands.remove_season_team_use_case import (
    RemoveSeasonTeamUseCase,
)
from modules.tournaments.application.queries.get_season_bracket_query import GetSeasonBracketQuery
from modules.tournaments.application.queries.get_season_query import GetSeasonQuery
from modules.tournaments.application.queries.get_season_standings_query import (
    GetSeasonStandingsQuery,
)
from modules.tournaments.application.queries.list_season_fixtures_query import (
    ListSeasonFixturesQuery,
)
from modules.tournaments.application.queries.list_seasons_query import ListSeasonsQuery


class SeasonViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="tournaments_seasons_create",
        request=CreateSeasonRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateTournamentSeasonResult", fields={"id": serializers.UUIDField()}
            )
        },
    )
    def create(self, request):
        request_contract = CreateSeasonRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateSeasonUseCase)
        entity_id = use_case.execute(**request_contract.validated_data)

        return Response({"id": str(entity_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="tournaments_seasons_list",
        parameters=[ListSeasonsRequest],
        responses={status.HTTP_200_OK: ListSeasonsResponse(many=True)},
    )
    def list(self, request):
        request_contract = ListSeasonsRequest(data=request.query_params)
        request_contract.is_valid(raise_exception=True)

        query = injector_instance.get(ListSeasonsQuery)
        result = query.execute(**request_contract.validated_data)

        return Response(ListSeasonsResponse(result, many=True).data)

    @extend_schema(
        operation_id="tournaments_seasons_retrieve",
        responses={status.HTTP_200_OK: GetSeasonResponse},
    )
    def retrieve(self, request, pk=None):
        query = injector_instance.get(GetSeasonQuery)
        result = query.execute(pk)

        return Response(GetSeasonResponse(result).data)

    @extend_schema(
        operation_id="tournaments_seasons_groups",
        responses={status.HTTP_200_OK: GetSeasonStandingsResponse(many=True)},
    )
    @action(detail=True, methods=["get"])
    def groups(self, request, pk=None):
        result = injector_instance.get(GetSeasonStandingsQuery).execute(pk)

        return Response(GetSeasonStandingsResponse(result, many=True).data)

    @extend_schema(
        operation_id="tournaments_seasons_bracket",
        responses={status.HTTP_200_OK: GetSeasonBracketResponse},
    )
    @action(detail=True, methods=["get"])
    def bracket(self, request, pk=None):
        result = injector_instance.get(GetSeasonBracketQuery).execute(pk)

        return Response(GetSeasonBracketResponse(result).data)

    @extend_schema(
        operation_id="tournaments_seasons_matches",
        responses={status.HTTP_200_OK: ListFixturesResponse(many=True)},
    )
    @action(detail=True, methods=["get"])
    def matches(self, request, pk=None):
        result = injector_instance.get(ListSeasonFixturesQuery).execute(pk)

        return Response(ListFixturesResponse(result, many=True).data)

    @extend_schema(
        operation_id="tournaments_season_add_team",
        request=SeasonTeamRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["post"], url_path="teams")
    def add_team(self, request, pk=None):
        contract = SeasonTeamRequest(data=request.data)
        contract.is_valid(raise_exception=True)

        injector_instance.get(AddSeasonTeamUseCase).execute(season_id=pk, **contract.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="tournaments_season_remove_team",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    @action(detail=True, methods=["delete"], url_path="teams/<uuid:team_id>")
    def remove_team(self, request, pk=None, team_id=None):
        injector_instance.get(RemoveSeasonTeamUseCase).execute(season_id=pk, team_id=team_id)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="tournaments_generate_bracket",
        request=GenerateBracketRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="GenerateBracketResult",
                fields={"phase_ids": serializers.ListField(child=serializers.UUIDField())},
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="generate-bracket")
    def generate_bracket(self, request, pk=None):
        contract = GenerateBracketRequest(data=request.data)
        contract.is_valid(raise_exception=True)

        phase_ids = injector_instance.get(GenerateBracketUseCase).execute(
            season_id=pk, **contract.validated_data
        )

        return Response(
            {"phase_ids": [str(value) for value in phase_ids]}, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        operation_id="tournaments_advance_bracket",
        request=None,
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="AdvanceBracketResult", fields={"created_matches": serializers.IntegerField()}
            )
        },
    )
    @action(detail=True, methods=["post"], url_path="advance-bracket")
    def advance_bracket(self, request, pk=None):
        created = injector_instance.get(AdvanceBracketUseCase).execute(season_id=pk)

        return Response({"created_matches": created})
