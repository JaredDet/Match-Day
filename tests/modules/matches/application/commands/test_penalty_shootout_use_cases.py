import pytest

from modules.matches.application.commands.reduce_penalty_shootout_participants_use_case import (
    ReducePenaltyShootoutParticipantsUseCase,
)
from modules.matches.application.commands.register_penalty_shootout_kick_use_case import (
    RegisterPenaltyShootoutKickUseCase,
)
from modules.matches.application.commands.start_penalty_shootout_use_case import (
    StartPenaltyShootoutUseCase,
)
from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.match_squad_player import MatchSquadPlayer
from modules.matches.domain.penalty_shootout import (
    PenaltyKickOutcome,
    PenaltyShootout,
    PenaltyShootoutDepartureReason,
    PenaltyShootoutIneligibilityReason,
    PenaltyShootoutParticipant,
    PenaltyShootoutStatus,
)
from modules.matches.errors import MatchErrors
from modules.matches.infrastructure.repository.match_repository import MatchRepository
from modules.matches.infrastructure.repository.match_squad_repository import (
    MatchSquadRepository,
)
from modules.matches.infrastructure.repository.penalty_shootout_repository import (
    PenaltyShootoutRepository,
)
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def create_match_with_eligible_players(*, home_count=2, away_count=2):
    match = MatchMother.create(
        persist_teams=True,
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
        current_minute=90,
    )
    match.save()
    players = {TeamSide.HOME: [], TeamSide.AWAY: []}

    for team_side, team_id, player_count in (
        (TeamSide.HOME, match.home_team_id, home_count),
        (TeamSide.AWAY, match.away_team_id, away_count),
    ):
        for index in range(player_count):
            player = Player.create(
                team_id=team_id,
                name=f"Lanzador {team_side.value} {index + 1}",
            )
            player.save()
            MatchSquadPlayer.create(
                match=match,
                player=player,
                team_side=team_side,
                shirt_number=index + 1,
            ).save()
            players[team_side].append(player)

    return match, players


def test_persists_starting_team_and_enforces_kicker_rotation():
    match, players = create_match_with_eligible_players()
    match_repository = MatchRepository()
    shootout_repository = PenaltyShootoutRepository()
    start_use_case = StartPenaltyShootoutUseCase(
        match_repository,
        MatchSquadRepository(),
        shootout_repository,
    )
    register_kick_use_case = RegisterPenaltyShootoutKickUseCase(
        match_repository,
        MatchSquadRepository(),
        shootout_repository,
    )

    start_use_case.execute(
        match_id=match.id,
        starting_team_side=TeamSide.AWAY,
    )
    shootout = PenaltyShootout.objects.get(match=match)

    assert shootout.starting_team_side == TeamSide.AWAY
    assert shootout.next_team_side == TeamSide.AWAY

    register_kick_use_case.execute(
        match_id=match.id,
        player_id=players[TeamSide.AWAY][0].id,
        outcome=PenaltyKickOutcome.SCORED,
    )
    register_kick_use_case.execute(
        match_id=match.id,
        player_id=players[TeamSide.HOME][0].id,
        outcome=PenaltyKickOutcome.SCORED,
    )

    with pytest.raises(type(MatchErrors.PenaltyShootoutKickerAlreadyUsed)):
        register_kick_use_case.execute(
            match_id=match.id,
            player_id=players[TeamSide.AWAY][0].id,
            outcome=PenaltyKickOutcome.SCORED,
        )

    register_kick_use_case.execute(
        match_id=match.id,
        player_id=players[TeamSide.AWAY][1].id,
        outcome=PenaltyKickOutcome.SCORED,
    )
    register_kick_use_case.execute(
        match_id=match.id,
        player_id=players[TeamSide.HOME][1].id,
        outcome=PenaltyKickOutcome.SCORED,
    )
    register_kick_use_case.execute(
        match_id=match.id,
        player_id=players[TeamSide.AWAY][0].id,
        outcome=PenaltyKickOutcome.SCORED,
    )

    assert shootout.kicks.filter(player=players[TeamSide.AWAY][0]).count() == 2


def test_requires_larger_team_to_exclude_exact_player_difference():
    match, players = create_match_with_eligible_players(home_count=3, away_count=2)
    shootout_repository = PenaltyShootoutRepository()
    use_case = StartPenaltyShootoutUseCase(
        MatchRepository(),
        MatchSquadRepository(),
        shootout_repository,
    )

    with pytest.raises(type(MatchErrors.InvalidPenaltyShootoutExclusions)):
        use_case.execute(
            match_id=match.id,
            starting_team_side=TeamSide.HOME,
        )

    excluded_player = players[TeamSide.HOME][2]
    shootout_id = use_case.execute(
        match_id=match.id,
        starting_team_side=TeamSide.HOME,
        equalization_excluded_player_ids=[excluded_player.id],
    )

    assert shootout_repository.list_participant_ids(
        shootout_id=shootout_id,
        team_side=TeamSide.HOME,
    ) == {player.id for player in players[TeamSide.HOME][:2]}
    assert (
        len(
            shootout_repository.list_participant_ids(
                shootout_id=shootout_id,
                team_side=TeamSide.AWAY,
            )
        )
        == 2
    )


def test_reduces_both_teams_when_participant_becomes_unavailable():
    match, players = create_match_with_eligible_players(home_count=3, away_count=3)
    match_repository = MatchRepository()
    shootout_repository = PenaltyShootoutRepository()
    StartPenaltyShootoutUseCase(
        match_repository,
        MatchSquadRepository(),
        shootout_repository,
    ).execute(
        match_id=match.id,
        starting_team_side=TeamSide.HOME,
    )

    ReducePenaltyShootoutParticipantsUseCase(
        match_repository,
        shootout_repository,
    ).execute(
        match_id=match.id,
        unavailable_player_id=players[TeamSide.HOME][0].id,
        departure_reason=PenaltyShootoutDepartureReason.INJURY,
        opponent_excluded_player_id=players[TeamSide.AWAY][0].id,
    )

    unavailable_participant = PenaltyShootoutParticipant.objects.get(
        shootout__match=match,
        player=players[TeamSide.HOME][0],
    )
    opponent_participant = PenaltyShootoutParticipant.objects.get(
        shootout__match=match,
        player=players[TeamSide.AWAY][0],
    )
    counts = shootout_repository.get_eligible_counts(
        unavailable_participant.shootout_id,
    )

    assert not unavailable_participant.is_eligible
    assert unavailable_participant.ineligibility_reason == PenaltyShootoutIneligibilityReason.INJURY
    assert not opponent_participant.is_eligible
    assert (
        opponent_participant.ineligibility_reason
        == PenaltyShootoutIneligibilityReason.OPPONENT_REDUCTION
    )
    assert counts == {TeamSide.HOME: 2, TeamSide.AWAY: 2}


def test_rejects_reduction_with_players_from_same_team():
    match, players = create_match_with_eligible_players(home_count=3, away_count=3)
    match_repository = MatchRepository()
    shootout_repository = PenaltyShootoutRepository()
    StartPenaltyShootoutUseCase(
        match_repository,
        MatchSquadRepository(),
        shootout_repository,
    ).execute(
        match_id=match.id,
        starting_team_side=TeamSide.HOME,
    )

    with pytest.raises(type(MatchErrors.InvalidPenaltyShootoutReduction)):
        ReducePenaltyShootoutParticipantsUseCase(
            match_repository,
            shootout_repository,
        ).execute(
            match_id=match.id,
            unavailable_player_id=players[TeamSide.HOME][0].id,
            departure_reason=PenaltyShootoutDepartureReason.INJURY,
            opponent_excluded_player_id=players[TeamSide.HOME][1].id,
        )


def test_rejects_reducing_an_ineligible_participant_twice():
    match, players = create_match_with_eligible_players(home_count=3, away_count=3)
    match_repository = MatchRepository()
    shootout_repository = PenaltyShootoutRepository()
    StartPenaltyShootoutUseCase(
        match_repository,
        MatchSquadRepository(),
        shootout_repository,
    ).execute(
        match_id=match.id,
        starting_team_side=TeamSide.HOME,
    )
    use_case = ReducePenaltyShootoutParticipantsUseCase(
        match_repository,
        shootout_repository,
    )
    use_case.execute(
        match_id=match.id,
        unavailable_player_id=players[TeamSide.HOME][0].id,
        departure_reason=PenaltyShootoutDepartureReason.INJURY,
        opponent_excluded_player_id=players[TeamSide.AWAY][0].id,
    )

    with pytest.raises(type(MatchErrors.InvalidPenaltyShootoutReduction)):
        use_case.execute(
            match_id=match.id,
            unavailable_player_id=players[TeamSide.HOME][0].id,
            departure_reason=PenaltyShootoutDepartureReason.INJURY,
            opponent_excluded_player_id=players[TeamSide.AWAY][1].id,
        )


def test_rejects_kick_from_participant_removed_during_shootout():
    match, players = create_match_with_eligible_players(home_count=3, away_count=3)
    match_repository = MatchRepository()
    shootout_repository = PenaltyShootoutRepository()
    squad_repository = MatchSquadRepository()
    StartPenaltyShootoutUseCase(
        match_repository,
        squad_repository,
        shootout_repository,
    ).execute(
        match_id=match.id,
        starting_team_side=TeamSide.HOME,
    )
    ReducePenaltyShootoutParticipantsUseCase(
        match_repository,
        shootout_repository,
    ).execute(
        match_id=match.id,
        unavailable_player_id=players[TeamSide.HOME][0].id,
        departure_reason=PenaltyShootoutDepartureReason.SENT_OFF,
        opponent_excluded_player_id=players[TeamSide.AWAY][0].id,
    )

    with pytest.raises(type(MatchErrors.InvalidPenaltyShootoutPlayer)):
        RegisterPenaltyShootoutKickUseCase(
            match_repository,
            squad_repository,
            shootout_repository,
        ).execute(
            match_id=match.id,
            player_id=players[TeamSide.HOME][0].id,
            outcome=PenaltyKickOutcome.MISSED,
        )


def test_rejects_participant_reduction_after_shootout_is_decided():
    match, players = create_match_with_eligible_players(home_count=2, away_count=2)
    match_repository = MatchRepository()
    shootout_repository = PenaltyShootoutRepository()
    StartPenaltyShootoutUseCase(
        match_repository,
        MatchSquadRepository(),
        shootout_repository,
    ).execute(
        match_id=match.id,
        starting_team_side=TeamSide.HOME,
    )
    shootout = PenaltyShootout.objects.get(match=match)
    shootout.status = PenaltyShootoutStatus.DECIDED
    shootout.winner_team_side = TeamSide.HOME
    shootout.save()

    with pytest.raises(type(MatchErrors.InvalidPenaltyShootoutReduction)):
        ReducePenaltyShootoutParticipantsUseCase(
            match_repository,
            shootout_repository,
        ).execute(
            match_id=match.id,
            unavailable_player_id=players[TeamSide.HOME][0].id,
            departure_reason=PenaltyShootoutDepartureReason.INJURY,
            opponent_excluded_player_id=players[TeamSide.AWAY][0].id,
        )
