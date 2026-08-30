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
from modules.teams.api.contracts.responses.get_player_response import GetPlayerResponse
from modules.teams.api.contracts.responses.get_team_response import GetTeamResponse
from modules.teams.api.contracts.responses.list_players_response import ListPlayersResponse
from modules.teams.api.contracts.responses.list_teams_response import ListTeamsResponse
from modules.teams.application.queries.get_player_query import GetPlayerQuery
from modules.teams.application.queries.get_team_query import GetTeamQuery
from modules.teams.application.queries.list_players_query import ListPlayersQuery
from modules.teams.application.queries.list_teams_query import ListTeamsQuery


class Command(BaseCommand):
    help = "Muestra los listados y detalles demostrativos de la V3"

    def handle(self, *args, **options):
        list_matches_query = injector_instance.get(ListMatchesQuery)
        get_match_query = injector_instance.get(GetMatchQuery)
        list_teams_query = injector_instance.get(ListTeamsQuery)
        get_team_query = injector_instance.get(GetTeamQuery)
        list_players_query = injector_instance.get(ListPlayersQuery)
        get_player_query = injector_instance.get(GetPlayerQuery)

        matches = list_matches_query.execute(status=MatchStatus.FINISHED)
        demo_match = find_demo_match()
        if demo_match is None:
            raise CommandError(
                "No existe el partido demo. Ejecuta primero: "
                "uv run python manage.py seed_demo_match"
            )
        try:
            match = get_match_query.execute(demo_match.id)
        except type(MatchErrors.NotFound) as error:
            raise CommandError("No fue posible consultar el partido demo") from error

        teams = list_teams_query.execute()
        team = get_team_query.execute(demo_match.home_team_id)
        players = list_players_query.execute(team_id=demo_match.home_team_id)
        player = get_player_query.execute(
            next((item.id for item in players if item.is_captain), players[0].id)
        )

        self.stdout.write("LIST MATCHES")
        self.stdout.write(self._render(ListMatchesResponse(matches, many=True).data))
        self.stdout.write("GET MATCH")
        self.stdout.write(self._render(GetMatchResponse(match).data))
        self.stdout.write("LIST TEAMS")
        self.stdout.write(self._render(ListTeamsResponse(teams, many=True).data))
        self.stdout.write("GET TEAM")
        self.stdout.write(self._render(GetTeamResponse(team).data))
        self.stdout.write("LIST PLAYERS")
        self.stdout.write(self._render(ListPlayersResponse(players, many=True).data))
        self.stdout.write("GET PLAYER")
        self.stdout.write(self._render(GetPlayerResponse(player).data))

    @staticmethod
    def _render(data) -> str:
        return JSONRenderer().render(data).decode("utf-8")
