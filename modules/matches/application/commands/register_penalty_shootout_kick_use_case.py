from uuid import UUID

from django.db import transaction
from injector import inject

from modules.matches.domain.match_event import TeamSide
from modules.matches.domain.penalty_shootout import PenaltyKickOutcome, PenaltyShootoutKick
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)
from modules.matches.infrastructure.repository.penalty_shootout_repository import (
    PenaltyShootoutRepository,
)


class RegisterPenaltyShootoutKickUseCase:
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
        player_id: UUID,
        outcome: PenaltyKickOutcome,
    ) -> UUID:
        match = self.match_repository.get_for_update(match_id)

        if match is None:
            raise MatchErrors.NotFound

        shootout = self.shootout_repository.get_for_update(match.id)

        if shootout is None:
            raise MatchErrors.PenaltyShootoutNotFound

        squad_player = self.squad_repository.get_for_update(
            match_id=match.id,
            player_id=player_id,
        )

        if squad_player is None:
            raise MatchErrors.InvalidPenaltyShootoutPlayer

        team_side = TeamSide(squad_player.team_side)

        eligible_counts = self.shootout_repository.get_eligible_counts(shootout.id)
        shootout.ensure_equal_participant_counts(
            home_eligible_count=eligible_counts[TeamSide.HOME],
            away_eligible_count=eligible_counts[TeamSide.AWAY],
        )

        eligible_player_ids = self.shootout_repository.list_participant_ids(
            shootout_id=shootout.id,
            team_side=team_side,
        )
        kick_counts = self.shootout_repository.get_player_kick_counts(
            shootout_id=shootout.id,
            team_side=team_side,
        )
        sequence_number = shootout.home_kick_count + shootout.away_kick_count + 1
        kick = PenaltyShootoutKick.create(
            shootout=shootout,
            squad_player=squad_player,
            sequence_number=sequence_number,
            outcome=outcome,
            eligible_player_ids=eligible_player_ids,
            kick_counts=kick_counts,
        )

        self.shootout_repository.save(shootout)
        self.shootout_repository.save_kick(kick)

        return kick.id
