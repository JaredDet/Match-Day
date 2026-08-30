from django.core.management.base import BaseCommand, CommandError
from rest_framework.renderers import JSONRenderer

from core.dependency_injector import injector_instance
from modules.matches.api.contracts.responses.get_match_response import GetMatchResponse
from modules.matches.api.contracts.responses.list_matches_response import ListMatchesResponse
from modules.matches.application.queries.get_match_query import GetMatchQuery
from modules.matches.application.queries.list_matches_query import ListMatchesQuery
from modules.matches.domain.match import MatchStatus
from modules.matches.errors import MatchErrors
from modules.matches.management.commands.seed_demo_match import find_demo_match


class Command(BaseCommand):
    help = "Muestra el listado y detalle del partido demostrativo de la V2"

    def handle(self, *args, **options):
        list_query = injector_instance.get(ListMatchesQuery)
        get_query = injector_instance.get(GetMatchQuery)

        matches = list_query.execute(status=MatchStatus.FINISHED)
        demo_match = find_demo_match()
        if demo_match is None:
            raise CommandError(
                "No existe el partido demo. Ejecuta primero: "
                "uv run python manage.py seed_demo_match"
            )
        try:
            match = get_query.execute(demo_match.id)
        except type(MatchErrors.NotFound) as error:
            raise CommandError("No fue posible consultar el partido demo") from error

        self.stdout.write("LIST MATCHES")
        self.stdout.write(self._render(ListMatchesResponse(matches, many=True).data))
        self.stdout.write("GET MATCH")
        self.stdout.write(self._render(GetMatchResponse(match).data))

    @staticmethod
    def _render(data) -> str:
        return JSONRenderer().render(data).decode("utf-8")
