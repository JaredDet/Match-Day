from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.tournaments.api.contracts.requests.create_fixture_request import CreateFixtureRequest
from modules.tournaments.api.contracts.requests.list_fixtures_request import ListFixturesRequest
from modules.tournaments.api.contracts.requests.update_fixture_request import UpdateFixtureRequest
from modules.tournaments.api.contracts.responses.get_fixture_response import GetFixtureResponse
from modules.tournaments.api.contracts.responses.list_fixtures_response import ListFixturesResponse
from modules.tournaments.application.commands.create_fixture_use_case import CreateFixtureUseCase
from modules.tournaments.application.commands.delete_fixture_use_case import DeleteFixtureUseCase
from modules.tournaments.application.commands.update_fixture_use_case import UpdateFixtureUseCase
from modules.tournaments.application.queries.get_fixture_query import GetFixtureQuery
from modules.tournaments.application.queries.list_fixtures_query import ListFixturesQuery


class FixtureViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="tournaments_fixtures_create",
        request=CreateFixtureRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateTournamentFixtureResult", fields={"id": serializers.UUIDField()}
            )
        },
    )
    def create(self, request):
        request_contract = CreateFixtureRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateFixtureUseCase)
        entity_id = use_case.execute(**request_contract.validated_data)

        return Response({"id": str(entity_id)}, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="tournaments_fixtures_list",
        parameters=[ListFixturesRequest],
        responses={status.HTTP_200_OK: ListFixturesResponse(many=True)},
    )
    def list(self, request):
        request_contract = ListFixturesRequest(data=request.query_params)
        request_contract.is_valid(raise_exception=True)

        query = injector_instance.get(ListFixturesQuery)
        result = query.execute(**request_contract.validated_data)

        return Response(ListFixturesResponse(result, many=True).data)

    @extend_schema(
        operation_id="tournaments_fixtures_retrieve",
        responses={status.HTTP_200_OK: GetFixtureResponse},
    )
    def retrieve(self, request, pk=None):
        query = injector_instance.get(GetFixtureQuery)
        result = query.execute(pk)

        return Response(GetFixtureResponse(result).data)

    @extend_schema(
        operation_id="tournaments_fixture_delete",
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def destroy(self, request, pk=None):
        use_case = injector_instance.get(DeleteFixtureUseCase)
        use_case.execute(fixture_id=pk)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="tournaments_fixture_update",
        request=UpdateFixtureRequest,
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def partial_update(self, request, pk=None):
        contract = UpdateFixtureRequest(data=request.data)
        contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(UpdateFixtureUseCase)
        use_case.execute(fixture_id=pk, **contract.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)
