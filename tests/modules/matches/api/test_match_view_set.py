from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from modules.matches.domain.card import CardType
from modules.matches.domain.match import Match, MatchFormation, MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.match_squad_player import (
    MatchSquadPlayer,
    MatchSquadRole,
)
from modules.matches.domain.match_substitution import MatchSubstitution
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team

pytestmark = pytest.mark.django_db


def _schedule_match(*, home_team_name, away_team_name, scheduled_at):
    home_team = Team.objects.create(name=home_team_name.strip())
    away_team = Team.objects.create(name=away_team_name.strip())
    return Match.schedule(
        home_team=home_team,
        away_team=away_team,
        scheduled_at=scheduled_at,
    )


def _create_player(match, team_side, name):
    team = match.home_team if team_side == TeamSide.HOME else match.away_team
    player = Player.objects.create(team=team, name=name)
    MatchSquadPlayer.objects.create(
        match=match,
        player=player,
        team_side=team_side,
        shirt_number=(
            MatchSquadPlayer.objects.filter(match=match, team_side=team_side).count()
            + 1
        ),
        is_on_field=True,
    )
    return player


def _prepare_match_for_start(match):
    match.set_formation(
        team_side=TeamSide.HOME,
        formation=MatchFormation.FOUR_THREE_THREE,
    )
    match.set_formation(
        team_side=TeamSide.AWAY,
        formation=MatchFormation.FOUR_FOUR_TWO,
    )
    match.save()
    for team_side in TeamSide:
        for index in range(1, 12):
            _create_player(match, team_side, f"{team_side} titular {index}")


def test_creates_match_through_injected_use_case():
    home_team = Team.objects.create(name="Colo-Colo")
    away_team = Team.objects.create(name="Universidad de Chile")
    response = APIClient().post(
        reverse("matches-list"),
        {
            "home_team_id": str(home_team.id),
            "away_team_id": str(away_team.id),
            "scheduled_at": (timezone.now() + timedelta(days=1)).isoformat(),
        },
        format="json",
    )

    assert response.status_code == 201
    match_id = UUID(response.data["id"])
    match = Match.objects.get(id=match_id)
    assert match.home_team == home_team
    assert match.away_team == away_team
    assert match.status == MatchStatus.SCHEDULED


def test_returns_domain_error_when_teams_are_equal():
    team = Team.objects.create(name="Colo-Colo")
    response = APIClient().post(
        reverse("matches-list"),
        {
            "home_team_id": str(team.id),
            "away_team_id": str(team.id),
            "scheduled_at": (timezone.now() + timedelta(days=1)).isoformat(),
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data == {
        "code": "invalid_match_teams",
        "message": "Los equipos deben ser diferentes",
    }


def test_rejects_duplicate_match_with_reversed_teams():
    scheduled_at = (timezone.now() + timedelta(days=1)).replace(microsecond=0)
    home_team = Team.objects.create(name="Colo-Colo")
    away_team = Team.objects.create(name="Universidad de Chile")
    Match.schedule(
        home_team=home_team,
        away_team=away_team,
        scheduled_at=scheduled_at,
    ).save()

    response = APIClient().post(
        reverse("matches-list"),
        {
            "home_team_id": str(away_team.id),
            "away_team_id": str(home_team.id),
            "scheduled_at": scheduled_at.isoformat(),
        },
        format="json",
    )

    assert response.status_code == 409
    assert response.data["code"] == "match_already_exists"


def test_formats_invalid_request_with_common_error_contract():
    home_team = Team.objects.create(name="Colo-Colo")
    away_team = Team.objects.create(name="Universidad de Chile")
    response = APIClient().post(
        reverse("matches-list"),
        {
            "home_team_id": str(home_team.id),
            "away_team_id": str(away_team.id),
            "scheduled_at": "not-a-date",
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["code"] == "validation_error"
    assert "scheduled_at" in response.data["details"]


def test_starts_scheduled_match_through_injected_use_case():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now() + timedelta(hours=1),
    )
    _prepare_match_for_start(match)

    response = APIClient().post(reverse("matches-start", args=[match.id]))

    assert response.status_code == 204
    assert response.content == b""
    match.refresh_from_db()
    assert match.status == MatchStatus.LIVE
    assert match.started_at is not None


def test_rejects_starting_match_twice():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.save()

    response = APIClient().post(reverse("matches-start", args=[match.id]))

    assert response.status_code == 409
    assert response.data["code"] == "invalid_match_state"


def test_returns_not_found_when_starting_unknown_match():
    response = APIClient().post(reverse("matches-start", args=[uuid4()]))

    assert response.status_code == 404
    assert response.data["code"] == "match_not_found"


def test_advances_match_through_halftime_and_second_half():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.save()

    url = reverse("matches-advance-period", args=[match.id])
    halftime_response = APIClient().post(
        url,
        {"expected_period": "first_half"},
        format="json",
    )
    repeated_response = APIClient().post(
        url,
        {"expected_period": "first_half"},
        format="json",
    )
    second_half_response = APIClient().post(
        url,
        {"expected_period": "halftime"},
        format="json",
    )

    assert halftime_response.status_code == 204
    assert repeated_response.status_code == 409
    assert repeated_response.data["code"] == "match_period_mismatch"
    assert second_half_response.status_code == 204
    match.refresh_from_db()
    assert match.current_period == "second_half"


def test_updates_match_clock_with_expected_period():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.save()

    response = APIClient().patch(
        reverse("matches-update-clock", args=[match.id]),
        {
            "expected_period": "first_half",
            "minute": 45,
            "added_minute": 2,
        },
        format="json",
    )

    assert response.status_code == 204
    match.refresh_from_db()
    assert match.current_minute == 45
    assert match.current_added_minute == 2


def test_finishes_live_match_through_injected_use_case():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.end_first_half()
    match.start_second_half()
    match.save()

    response = APIClient().post(reverse("matches-finish", args=[match.id]))

    assert response.status_code == 204
    assert response.content == b""
    match.refresh_from_db()
    assert match.status == MatchStatus.FINISHED
    assert match.finished_at is not None


def test_rejects_finishing_match_that_is_not_live():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()

    response = APIClient().post(reverse("matches-finish", args=[match.id]))

    assert response.status_code == 409
    assert response.data["code"] == "invalid_match_state"


def test_returns_not_found_when_finishing_unknown_match():
    response = APIClient().post(reverse("matches-finish", args=[uuid4()]))

    assert response.status_code == 404
    assert response.data["code"] == "match_not_found"


def test_registers_goal_and_updates_score_through_injected_use_case():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.update_clock(expected_period=MatchPeriod.FIRST_HALF, minute=34)
    match.save()
    player = _create_player(match, TeamSide.HOME, "Goleador Local")

    response = APIClient().post(
        reverse("matches-register-goal", args=[match.id]),
        {
            "player_id": str(player.id),
            "minute": 34,
        },
        format="json",
    )

    assert response.status_code == 201
    goal = match.goals.get(id=UUID(response.data["id"]))
    assert goal.player_name == "Goleador Local"
    match.refresh_from_db()
    assert match.home_goal_count == 1
    assert match.away_goal_count == 0


def test_rejects_goal_when_match_is_not_live():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()
    player = _create_player(match, TeamSide.HOME, "Jugador")

    response = APIClient().post(
        reverse("matches-register-goal", args=[match.id]),
        {"player_id": str(player.id), "minute": 1},
        format="json",
    )

    assert response.status_code == 409
    assert response.data["code"] == "invalid_match_state"
    assert match.goals.count() == 0


def test_registers_card_and_updates_counter_through_injected_use_case():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.end_first_half()
    match.start_second_half()
    match.update_clock(expected_period=MatchPeriod.SECOND_HALF, minute=80)
    match.save()
    player = _create_player(match, TeamSide.AWAY, "Defensor visitante")

    response = APIClient().post(
        reverse("matches-register-card", args=[match.id]),
        {
            "player_id": str(player.id),
            "card_type": CardType.RED,
            "minute": 80,
        },
        format="json",
    )

    assert response.status_code == 201
    card = match.cards.get(id=UUID(response.data["id"]))
    assert card.card_type == CardType.RED
    match.refresh_from_db()
    assert match.home_card_count == 0
    assert match.away_card_count == 1


def test_rejects_card_when_match_is_not_live():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()
    player = _create_player(match, TeamSide.HOME, "Jugador")

    response = APIClient().post(
        reverse("matches-register-card", args=[match.id]),
        {
            "player_id": str(player.id),
            "card_type": CardType.YELLOW,
            "minute": 1,
        },
        format="json",
    )

    assert response.status_code == 409
    assert response.data["code"] == "invalid_match_state"


def test_registers_substitution_and_updates_players_on_field():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()
    player_out = Player.objects.create(team=match.home_team, name="Titular")
    player_in = Player.objects.create(team=match.home_team, name="Suplente")
    match.add_squad_player(player=player_out, shirt_number=7).save()
    match.add_squad_player(
        player=player_in,
        shirt_number=18,
        role=MatchSquadRole.SUBSTITUTE,
    ).save()
    match.start()
    match.end_first_half()
    match.start_second_half()
    match.update_clock(expected_period=MatchPeriod.SECOND_HALF, minute=62)
    match.save()

    response = APIClient().post(
        reverse("matches-register-substitution", args=[match.id]),
        {
            "player_out_id": str(player_out.id),
            "player_in_id": str(player_in.id),
            "minute": 60,
        },
        format="json",
    )

    assert response.status_code == 201
    substitution = MatchSubstitution.objects.get(id=response.data["id"])
    assert substitution.player_out.player == player_out
    assert substitution.player_in.player == player_in
    substitution.player_out.refresh_from_db()
    substitution.player_in.refresh_from_db()
    assert substitution.player_out.is_on_field is False
    assert substitution.player_in.is_on_field is True

    detail = APIClient().get(reverse("matches-detail", args=[match.id]))
    substitution_event = detail.data["events"][0]
    assert substitution_event == {
        "id": str(substitution.id),
        "type": "substitution",
        "team_side": TeamSide.HOME,
        "period": "second_half",
        "minute": 60,
        "added_minute": 0,
        "player_out_id": str(player_out.id),
        "player_out_name": "Titular",
        "player_in_id": str(player_in.id),
        "player_in_name": "Suplente",
    }
    assert [player["is_on_field"] for player in detail.data["home_team"]["lineup"]] == [
        False,
        True,
    ]

    incoming_goal = APIClient().post(
        reverse("matches-register-goal", args=[match.id]),
        {"player_id": str(player_in.id), "minute": 61},
        format="json",
    )
    outgoing_goal = APIClient().post(
        reverse("matches-register-goal", args=[match.id]),
        {"player_id": str(player_out.id), "minute": 62},
        format="json",
    )

    assert incoming_goal.status_code == 201
    assert outgoing_goal.status_code == 400
    assert outgoing_goal.data["code"] == "player_not_on_field"
    assert match.cards.count() == 0


def test_disallows_goal_and_decrements_score_through_injected_use_case():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.update_clock(expected_period=MatchPeriod.FIRST_HALF, minute=34)
    player = _create_player(match, TeamSide.HOME, "Goleador Local")
    goal = match.register_goal(
        player=player,
        minute=34,
    )
    match.save()
    goal.save()

    response = APIClient().post(reverse("matches-disallow-goal", args=[match.id, goal.id]))

    assert response.status_code == 204
    goal.refresh_from_db()
    match.refresh_from_db()
    assert goal.disallowed_at is not None
    assert match.home_goal_count == 0


def test_rejects_disallowing_goal_twice():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.update_clock(expected_period=MatchPeriod.FIRST_HALF, minute=40)
    player = _create_player(match, TeamSide.AWAY, "Goleador Visitante")
    goal = match.register_goal(
        player=player,
        minute=40,
    )
    match.save()
    goal.save()

    first_response = APIClient().post(reverse("matches-disallow-goal", args=[match.id, goal.id]))
    response = APIClient().post(reverse("matches-disallow-goal", args=[match.id, goal.id]))

    assert first_response.status_code == 204
    assert response.status_code == 409
    assert response.data["code"] == "goal_already_disallowed"
    match.refresh_from_db()
    assert match.away_goal_count == 0


def test_rescinds_card_and_decrements_counter_through_injected_use_case():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.end_first_half()
    match.start_second_half()
    match.update_clock(expected_period=MatchPeriod.SECOND_HALF, minute=51)
    player = _create_player(match, TeamSide.AWAY, "Defensor Visitante")
    card = match.register_card(
        player=player,
        card_type=CardType.YELLOW,
        minute=51,
    )
    match.save()
    card.save()

    response = APIClient().post(reverse("matches-rescind-card", args=[match.id, card.id]))

    assert response.status_code == 204
    card.refresh_from_db()
    match.refresh_from_db()
    assert card.rescinded_at is not None
    assert match.away_card_count == 0


def test_rejects_rescinding_card_twice():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.end_first_half()
    match.start_second_half()
    match.update_clock(expected_period=MatchPeriod.SECOND_HALF, minute=80)
    player = _create_player(match, TeamSide.HOME, "Defensor Local")
    card = match.register_card(
        player=player,
        card_type=CardType.RED,
        minute=80,
    )
    match.save()
    card.save()

    first_response = APIClient().post(reverse("matches-rescind-card", args=[match.id, card.id]))
    response = APIClient().post(reverse("matches-rescind-card", args=[match.id, card.id]))

    assert first_response.status_code == 204
    assert response.status_code == 409
    assert response.data["code"] == "card_already_rescinded"
    match.refresh_from_db()
    assert match.home_card_count == 0


def test_gets_match_detail_with_unified_event_timeline():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.start()
    match.update_clock(expected_period=MatchPeriod.FIRST_HALF, minute=30)
    goal_player = _create_player(match, TeamSide.HOME, "Goleador Local")
    card_player = _create_player(match, TeamSide.AWAY, "Defensor Visitante")
    goal = match.register_goal(
        player=goal_player,
        minute=30,
    )
    match.end_first_half()
    match.start_second_half()
    match.update_clock(expected_period=MatchPeriod.SECOND_HALF, minute=70)
    card = match.register_card(
        player=card_player,
        card_type=CardType.RED,
        minute=70,
    )
    match.save()
    goal.save()
    card.save()

    response = APIClient().get(reverse("matches-detail", args=[match.id]))

    assert response.status_code == 200
    assert response.data["status"] == MatchStatus.LIVE
    assert response.data["home_team"] == {
        "id": str(match.home_team_id),
        "name": "Colo-Colo",
        "team_side": TeamSide.HOME,
        "goals": 1,
        "formation": None,
        "lineup": [
            {
                "player_id": str(goal_player.id),
                "player_name": "Goleador Local",
                "shirt_number": 1,
                "role": "starter",
                "is_on_field": True,
                "is_sent_off": False,
                "sent_off_reason": None,
                "is_captain": False,
            }
        ],
    }
    assert response.data["away_team"] == {
        "id": str(match.away_team_id),
        "name": "Universidad de Chile",
        "team_side": TeamSide.AWAY,
        "goals": 0,
        "formation": None,
        "lineup": [
            {
                "player_id": str(card_player.id),
                "player_name": "Defensor Visitante",
                "shirt_number": 1,
                "role": "starter",
                "is_on_field": True,
                "is_sent_off": False,
                "sent_off_reason": None,
                "is_captain": False,
            }
        ],
    }
    assert [event["type"] for event in response.data["events"]] == [
        "goal",
        "red_card",
    ]
    assert response.data["events"][0]["id"] == str(goal.id)
    assert response.data["events"][0]["player_id"] == str(goal_player.id)


def test_returns_not_found_when_getting_unknown_match():
    response = APIClient().get(reverse("matches-detail", args=[uuid4()]))

    assert response.status_code == 404
    assert response.data["code"] == "match_not_found"


def test_updates_match_details_through_injected_use_case():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()

    response = APIClient().patch(
        reverse("matches-update-details", args=[match.id]),
        {"stadium_name": " Estadio Monumental ", "referee_name": "Piero Maza"},
        format="json",
    )

    assert response.status_code == 204
    match.refresh_from_db()
    assert match.stadium_name == "Estadio Monumental"
    assert match.referee_name == "Piero Maza"


def test_lists_matches_filtered_by_status_and_date():
    included = _schedule_match(
        home_team_name="Equipo Local",
        away_team_name="Equipo Visitante",
        scheduled_at=datetime(2026, 8, 30, 20, tzinfo=UTC),
    )
    included.start()
    excluded = _schedule_match(
        home_team_name="Otro Local",
        away_team_name="Otro Visitante",
        scheduled_at=datetime(2026, 8, 31, 20, tzinfo=UTC),
    )
    excluded.start()
    included.save()
    excluded.save()

    response = APIClient().get(
        reverse("matches-list"),
        {"status": "live", "date": "2026-08-30"},
    )

    assert response.status_code == 200
    assert response.data == [
        {
            "id": str(included.id),
            "status": "live",
            "current_period": "first_half",
            "current_minute": 1,
            "current_added_minute": 0,
            "scheduled_at": "2026-08-30T20:00:00Z",
            "home_team": {
                "id": str(included.home_team_id),
                "name": "Equipo Local",
                "team_side": TeamSide.HOME,
                "goals": 0,
                "formation": None,
            },
            "away_team": {
                "id": str(included.away_team_id),
                "name": "Equipo Visitante",
                "team_side": TeamSide.AWAY,
                "goals": 0,
                "formation": None,
            },
        }
    ]


def test_rejects_invalid_match_list_filters():
    response = APIClient().get(reverse("matches-list"), {"status": "paused"})

    assert response.status_code == 400
    assert response.data["code"] == "validation_error"
    assert "status" in response.data["details"]


def test_sets_and_replaces_match_lineup_with_formation():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()
    players = [
        Player.objects.create(team=match.home_team, name=f"Jugador {index}")
        for index in range(1, 12)
    ]
    substitutes = [
        Player.objects.create(team=match.home_team, name=f"Suplente {index}")
        for index in range(1, 3)
    ]
    match.home_team.captain = players[0]
    match.home_team.save()

    response = APIClient().put(
        reverse("matches-set-lineup", args=[match.id, TeamSide.HOME]),
        {
            "formation": MatchFormation.FOUR_THREE_THREE,
            "players": [
                {
                    "player_id": str(player.id),
                    "shirt_number": index,
                }
                for index, player in enumerate(players, start=1)
            ],
            "substitutes": [
                {
                    "player_id": str(player.id),
                    "shirt_number": index + 11,
                }
                for index, player in enumerate(substitutes, start=1)
            ],
        },
        format="json",
    )

    assert response.status_code == 204
    match.refresh_from_db()
    assert match.home_formation == MatchFormation.FOUR_THREE_THREE
    assert (
        MatchSquadPlayer.objects.filter(
            match=match,
            team_side=TeamSide.HOME,
        ).count()
        == 13
    )
    assert (
        MatchSquadPlayer.objects.get(
            match=match,
            team_side=TeamSide.HOME,
            is_captain=True,
        ).player
        == players[0]
    )

    response = APIClient().put(
        reverse("matches-set-lineup", args=[match.id, TeamSide.HOME]),
        {
            "formation": MatchFormation.FOUR_FOUR_TWO,
            "captain_id": str(players[1].id),
            "players": [
                {
                    "player_id": str(player.id),
                    "shirt_number": index + 20,
                }
                for index, player in enumerate(players, start=1)
            ],
        },
        format="json",
    )

    assert response.status_code == 204
    match.refresh_from_db()
    assert match.home_formation == MatchFormation.FOUR_FOUR_TWO
    lineup = MatchSquadPlayer.objects.filter(match=match, team_side=TeamSide.HOME)
    assert lineup.count() == 11
    assert lineup.get(is_captain=True).player == players[1]


def test_rejects_substitute_as_match_captain():
    match = _schedule_match(
        home_team_name="Colo-Colo",
        away_team_name="Universidad de Chile",
        scheduled_at=timezone.now(),
    )
    match.save()
    starters = [
        Player.objects.create(team=match.home_team, name=f"Titular {index}")
        for index in range(1, 12)
    ]
    substitute = Player.objects.create(team=match.home_team, name="Suplente")

    response = APIClient().put(
        reverse("matches-set-lineup", args=[match.id, TeamSide.HOME]),
        {
            "formation": MatchFormation.FOUR_THREE_THREE,
            "captain_id": str(substitute.id),
            "players": [
                {"player_id": str(player.id), "shirt_number": index}
                for index, player in enumerate(starters, start=1)
            ],
            "substitutes": [
                {"player_id": str(substitute.id), "shirt_number": 18}
            ],
        },
        format="json",
    )

    assert response.status_code == 400
    assert response.data["code"] == "invalid_lineup_captain"
