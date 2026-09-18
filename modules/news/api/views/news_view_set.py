from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.dependency_injector import injector_instance
from modules.news.api.contracts.requests.create_news_request import CreateNewsRequest
from modules.news.application.commands.create_news_use_case import CreateNewsUseCase


class NewsViewSet(ViewSet):
    lookup_value_converter = "uuid"

    @extend_schema(
        operation_id="news_create",
        request=CreateNewsRequest,
        responses={
            status.HTTP_201_CREATED: inline_serializer(
                name="CreateNewsResult",
                fields={"id": serializers.UUIDField()},
            )
        },
    )
    def create(self, request):
        request_contract = CreateNewsRequest(data=request.data)
        request_contract.is_valid(raise_exception=True)

        use_case = injector_instance.get(CreateNewsUseCase)
        news_id = use_case.execute(**request_contract.validated_data)
        return Response({"id": str(news_id)}, status=status.HTTP_201_CREATED)
