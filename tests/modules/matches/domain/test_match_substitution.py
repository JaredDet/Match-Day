import pytest

from modules.matches.domain.match import MatchStatus
from modules.matches.domain.match_event import MatchPeriod
from modules.matches.domain.match_squad_player import MatchSquadRole
from modules.matches.domain.match_substitution import MatchSubstitution
from modules.matches.errors import MatchErrors
from modules.teams.domain.player import Player
from tests.mothers.matches.match_mother import MatchMother


def test_substitutes_player_and_updates_on_field_state():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
    )
    player_out = Player.create(team_id=match.home_team_id, name="Titular")
    player_in = Player.create(team_id=match.home_team_id, name="Suplente")
    squad_player_out = match.add_squad_player(player=player_out, shirt_number=7)
    squad_player_in = match.add_squad_player(
        player=player_in,
        shirt_number=18,
        role=MatchSquadRole.SUBSTITUTE,
    )

    substitution = MatchSubstitution.create(
        match=match,
        player_out=squad_player_out,
        player_in=squad_player_in,
        minute=60,
    )

    assert substitution.minute == 60
    assert squad_player_out.is_on_field is False
    assert squad_player_in.is_on_field is True


def test_rejects_outgoing_player_who_is_not_on_field():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
    )
    first_substitute = Player.create(team_id=match.home_team_id, name="Suplente uno")
    second_substitute = Player.create(team_id=match.home_team_id, name="Suplente dos")
    player_out = match.add_squad_player(
        player=first_substitute,
        shirt_number=18,
        role=MatchSquadRole.SUBSTITUTE,
    )
    player_in = match.add_squad_player(
        player=second_substitute,
        shirt_number=19,
        role=MatchSquadRole.SUBSTITUTE,
    )

    with pytest.raises(type(MatchErrors.InvalidOutgoingPlayer)):
        MatchSubstitution.create(
            match=match,
            player_out=player_out,
            player_in=player_in,
            minute=60,
        )


def test_rejects_starter_as_incoming_player():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
    )
    first = Player.create(team_id=match.home_team_id, name="Titular uno")
    second = Player.create(team_id=match.home_team_id, name="Titular dos")
    player_out = match.add_squad_player(player=first, shirt_number=7)
    player_in = match.add_squad_player(player=second, shirt_number=8)

    with pytest.raises(type(MatchErrors.InvalidSubstitutePlayer)):
        MatchSubstitution.create(
            match=match,
            player_out=player_out,
            player_in=player_in,
            minute=60,
        )


def test_rejects_players_from_different_teams():
    match = MatchMother.create(
        status=MatchStatus.LIVE,
        current_period=MatchPeriod.SECOND_HALF,
    )
    home_player = Player.create(team_id=match.home_team_id, name="Titular local")
    away_player = Player.create(team_id=match.away_team_id, name="Suplente visitante")
    player_out = match.add_squad_player(player=home_player, shirt_number=7)
    player_in = match.add_squad_player(
        player=away_player,
        shirt_number=18,
        role=MatchSquadRole.SUBSTITUTE,
    )

    with pytest.raises(type(MatchErrors.InvalidSubstitutionPlayers)):
        MatchSubstitution.create(
            match=match,
            player_out=player_out,
            player_in=player_in,
            minute=60,
        )
