from uuid import UUID

from django.db import transaction
from injector import inject

from modules.tournaments.constants import DEFAULT_MAX_TEAMS_PER_GROUP
from modules.tournaments.domain.tournament import Tournament
from modules.tournaments.infrastructure.repository.tournament_repository import TournamentRepository


class CreateTournamentUseCase:
    @inject
    def __init__(self, tournament_repository: TournamentRepository):
        self.tournament_repository = tournament_repository

    @transaction.atomic
    def execute(
        self,
        *,
        slug: str,
        name: str,
        country: str,
        category: str,
        logo=None,
        max_teams_per_group: int = DEFAULT_MAX_TEAMS_PER_GROUP,
    ) -> UUID:
        tournament = Tournament.create(
            slug=slug,
            name=name,
            country=country,
            category=category,
            logo=logo,
            max_teams_per_group=max_teams_per_group,
        )

        self.tournament_repository.save(tournament)

        return tournament.id
