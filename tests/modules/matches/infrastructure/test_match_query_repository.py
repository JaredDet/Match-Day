from datetime import UTC, date, datetime
from uuid import uuid4

import pytest

from modules.matches.domain.card import CardType
from modules.matches.domain.match import MatchFormation, MatchStatus
from modules.matches.domain.match_event import TeamSide
from modules.matches.infrastructure.query_repository.match_query_repository import (
    MatchQueryRepository,
)
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother

pytestmark = pytest.mark.django_db


def test_builds_chronological_match_detail_without_disallowed_events():
    match = MatchMother.create(status=MatchStatus.LIVE, persist_teams=True)
    match.set_formation(
        team_side=TeamSide.HOME,
        formation=MatchFormation.FOUR_THREE_THREE,
    )
    match.set_formation(
        team_side=TeamSide.AWAY,
        formation=MatchFormation.FOUR_FOUR_TWO,
    )
    home_player = Player.objects.create(team=match.home_team, name="Goleador")
    away_player = Player.objects.create(team=match.away_team, name="Defensor")
    cancelled_player = Player.objects.create(team=match.away_team, name="Gol anulado")
    late_goal = match.register_goal(
        player=home_player,
        minute=60,
    )
    early_card = match.register_card(
        player=away_player,
        card_type=CardType.YELLOW,
        minute=20,
    )
    disallowed_goal = match.register_goal(
        player=cancelled_player,
        minute=10,
    )
    match.disallow_goal(disallowed_goal)
    lineup_player = match.add_lineup_player(
        player=home_player,
        shirt_number=9,
        is_captain=True,
    )
    match.save()
    lineup_player.save()
    late_goal.save()
    early_card.save()
    disallowed_goal.save()

    result = MatchQueryRepository().get(match.id)

    assert result.home_team.name == match.home_team.name
    assert result.home_team.id == match.home_team_id
    assert result.home_team.goals == 1
    assert result.away_team.goals == 0
    assert result.home_team.formation == MatchFormation.FOUR_THREE_THREE
    assert result.away_team.formation == MatchFormation.FOUR_FOUR_TWO
    assert len(result.lineup) == 1
    assert result.lineup[0].player_id == home_player.id
    assert result.lineup[0].shirt_number == 9
    assert result.lineup[0].is_captain is True
    assert [event.type for event in result.events] == ["yellow_card", "goal"]
    assert [event.minute for event in result.events] == [20, 60]
    assert [event.player_id for event in result.events] == [away_player.id, home_player.id]


def test_returns_none_when_match_does_not_exist():
    assert MatchQueryRepository().get(uuid4()) is None


def test_match_detail_keeps_team_name_snapshot_after_team_is_renamed():
    match = MatchMother.create(persist_teams=True)
    match.save()
    match.home_team.rename("Nombre nuevo")
    match.home_team.save()

    result = MatchQueryRepository().get(match.id)

    assert result.home_team.name == "Colo-Colo"


def test_lists_matches_filtered_by_status_and_date_in_scheduled_order():
    later = MatchMother.create(
        home_team_name="Equipo C",
        away_team_name="Equipo D",
        scheduled_at=datetime(2026, 8, 30, 22, tzinfo=UTC),
        status=MatchStatus.LIVE,
        persist_teams=True,
    )
    earlier = MatchMother.create(
        home_team_name="Equipo A",
        away_team_name="Equipo B",
        scheduled_at=datetime(2026, 8, 30, 18, tzinfo=UTC),
        status=MatchStatus.LIVE,
        persist_teams=True,
    )
    different_status = MatchMother.create(
        home_team_name="Equipo E",
        away_team_name="Equipo F",
        scheduled_at=datetime(2026, 8, 30, 20, tzinfo=UTC),
        persist_teams=True,
    )
    different_date = MatchMother.create(
        home_team_name="Equipo G",
        away_team_name="Equipo H",
        scheduled_at=datetime(2026, 8, 31, 18, tzinfo=UTC),
        status=MatchStatus.LIVE,
        persist_teams=True,
    )
    for match in (later, earlier, different_status, different_date):
        match.save()

    result = MatchQueryRepository().list(
        status=MatchStatus.LIVE,
        date=date(2026, 8, 30),
    )

    assert [match.id for match in result] == [earlier.id, later.id]
