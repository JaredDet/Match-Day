from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.penalty_shootout import (
    PenaltyShootout,
    PenaltyShootoutIneligibilityReason,
    PenaltyShootoutParticipant,
)
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)
from modules.matches.infrastructure.repository.penalty_shootout_repository import (
    PenaltyShootoutRepository,
)


class StartPenaltyShootoutUseCase:
    @inject
    def __init__(
        self,
        match_repository: MatchRepository,
        squad_repository: MatchSquadRepository,
        shootout_repository: PenaltyShootoutRepository,
    ):
        self.match_repository = match_repository
        self.squad_repository = squad_repository
        self.shootout_repository = shootout_repository

    @transaction.atomic
    def execute(
        self,
        *,
        match_id: UUID,
        starting_team_side: TeamSide,
        equalization_excluded_player_ids: list[UUID] | tuple[UUID, ...] = (),
    ) -> UUID:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        if self.shootout_repository.exists(match.id):
            raise MatchErrors.PenaltyShootoutAlreadyExists

        shootout = PenaltyShootout.start(
            match=match,
            starting_team_side=starting_team_side,
        )

        eligible_player_ids = {
            team_side: self.squad_repository.list_eligible_player_ids(
                match_id=match.id,
                team_side=team_side,
            )
            for team_side in TeamSide
        }
        participant_ids = shootout.equalize_eligible_players(
            home_player_ids=eligible_player_ids[TeamSide.HOME],
            away_player_ids=eligible_player_ids[TeamSide.AWAY],
            excluded_player_ids=set(equalization_excluded_player_ids),
        )

        self.shootout_repository.save(shootout)
        self.shootout_repository.save_participants(
            [
                PenaltyShootoutParticipant(
                    shootout=shootout,
                    player_id=player_id,
                    team_side=team_side,
                    is_eligible=player_id in participant_ids[team_side],
                    ineligibility_reason=(
                        None
                        if player_id in participant_ids[team_side]
                        else PenaltyShootoutIneligibilityReason.INITIAL_EQUALIZATION
                    ),
                    became_ineligible_at=(
                        None if player_id in participant_ids[team_side] else shootout.started_at
                    ),
                )
                for team_side, player_ids in eligible_player_ids.items()
                for player_id in player_ids
            ]
        )

        return shootout.id
