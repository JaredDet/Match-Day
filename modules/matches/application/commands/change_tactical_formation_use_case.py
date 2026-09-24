from django.db import transaction
from injector import inject

from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import MatchSquadRepository


class ChangeTacticalFormationUseCase:
    @inject
    def __init__(self, matches: MatchRepository, squads: MatchSquadRepository):
        self.matches, self.squads = matches, squads

    @transaction.atomic
    def execute(self, *, match_id, team_side, formation, positions):
        match = self.matches.get_for_update(match_id)
        if match is None:
            raise MatchErrors.NotFound
        players = self.squads.list_on_field_for_update(match_id=match_id, team_side=team_side)
        by_id = {player.player_id: player for player in players}
        if set(by_id) != {position["player_id"] for position in positions}:
            raise MatchErrors.InvalidLineupSize
        for position in positions:
            player = by_id[position["player_id"]]
            player.position_x = position["position_x"]
            player.position_y = position["position_y"]
        match.change_tactical_formation(team_side=team_side, formation=formation)
        self.matches.save(match)
        self.squads.save_all(players)
