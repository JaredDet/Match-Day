from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.dependency_injector import injector_instance
from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.application.commands.disallow_goal_use_case import DisallowGoalUseCase
from modules.matches.application.commands.finish_match_use_case import FinishMatchUseCase
from modules.matches.application.commands.register_card_use_case import RegisterCardUseCase
from modules.matches.application.commands.register_goal_use_case import RegisterGoalUseCase
from modules.matches.application.commands.rescind_card_use_case import RescindCardUseCase
from modules.matches.application.commands.set_match_lineup_use_case import (
    LineupPlayerInput,
    SetMatchLineupUseCase,
)
from modules.matches.application.commands.start_match_use_case import StartMatchUseCase
from modules.matches.domain.card import CardType
from modules.matches.domain.match import Match, MatchFormation
from modules.matches.domain.match_event import TeamSide
from modules.teams.application.commands.create_team_use_case import CreateTeamUseCase
from modules.teams.application.commands.register_team_squad_use_case import (
    RegisterTeamSquadUseCase,
)
from modules.teams.application.commands.update_team_use_case import UpdateTeamUseCase
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team

HOME_TEAM_NAME = "Atlético del Puerto"
HOME_TEAM_CURRENT_NAME = "Atlético Bahía"
AWAY_TEAM_NAME = "Deportivo Cordillera"
UNION_TEAM_NAME = "Unión del Valle"
SPORTING_TEAM_NAME = "Sporting del Bosque"
SCHEDULED_AT = datetime(2026, 8, 30, 20, tzinfo=UTC)
STADIUM_NAME = "Estadio del Horizonte"

TEAM_PLAYERS = {
    HOME_TEAM_NAME: [
        "Mateo Rojas",
        "Nicolás Vega",
        "Tomás Fuentes",
        "Diego Salazar",
        "Benjamín Soto",
        "Joaquín Morales",
        "Vicente Araya",
        "Martín Paredes",
        "Lucas Contreras",
        "Gabriel Navarro",
        "Sebastián Leiva",
    ],
    AWAY_TEAM_NAME: [
        "Felipe Cárdenas",
        "Cristóbal Muñoz",
        "Maximiliano Reyes",
        "Agustín Herrera",
        "Ignacio Silva",
        "Renato Valdés",
        "Bruno Espinoza",
        "Simón Carrasco",
        "Emiliano Godoy",
        "Franco Bustos",
        "Alonso Tapia",
    ],
    UNION_TEAM_NAME: [
        "Daniel Acuña",
        "Pablo Alarcón",
        "Matías Bravo",
        "Andrés Correa",
        "Samuel Delgado",
        "Esteban Figueroa",
        "Rodrigo Lagos",
        "Manuel Olivares",
        "César Peña",
        "Hugo Ramírez",
        "Leonardo Vera",
    ],
    SPORTING_TEAM_NAME: [
        "Adrián Campos",
        "Fabián Duarte",
        "Gonzalo Escobar",
        "Iván Flores",
        "Kevin Garrido",
        "Lautaro Hidalgo",
        "Marco Jara",
        "Nahuel Loyola",
        "Oscar Méndez",
        "Patricio Núñez",
        "Rubén Orellana",
    ],
}


@dataclass(frozen=True, slots=True)
class DemoFixture:
    home: str
    away: str
    scheduled_at: datetime
    stadium: str
    score: tuple[int, int] | None


FIXTURES = (
    DemoFixture(
        AWAY_TEAM_NAME,
        HOME_TEAM_NAME,
        datetime(2026, 7, 20, 20, tzinfo=UTC),
        "Estadio Cordillera",
        (0, 1),
    ),
    DemoFixture(
        UNION_TEAM_NAME,
        SPORTING_TEAM_NAME,
        datetime(2026, 7, 27, 18, tzinfo=UTC),
        "Estadio del Valle",
        (2, 2),
    ),
    DemoFixture(
        HOME_TEAM_NAME,
        UNION_TEAM_NAME,
        datetime(2026, 8, 3, 20, tzinfo=UTC),
        "Estadio del Horizonte",
        (3, 0),
    ),
    DemoFixture(
        SPORTING_TEAM_NAME,
        AWAY_TEAM_NAME,
        datetime(2026, 8, 10, 17, tzinfo=UTC),
        "Parque del Bosque",
        (1, 2),
    ),
    DemoFixture(
        AWAY_TEAM_NAME,
        UNION_TEAM_NAME,
        datetime(2026, 8, 17, 20, tzinfo=UTC),
        "Estadio Cordillera",
        (2, 1),
    ),
    DemoFixture(HOME_TEAM_NAME, AWAY_TEAM_NAME, SCHEDULED_AT, STADIUM_NAME, (2, 1)),
    DemoFixture(
        UNION_TEAM_NAME,
        HOME_TEAM_NAME,
        datetime(2026, 9, 6, 20, tzinfo=UTC),
        "Estadio del Valle",
        None,
    ),
    DemoFixture(
        AWAY_TEAM_NAME,
        SPORTING_TEAM_NAME,
        datetime(2026, 9, 7, 18, tzinfo=UTC),
        "Estadio Cordillera",
        None,
    ),
    DemoFixture(
        HOME_TEAM_NAME,
        SPORTING_TEAM_NAME,
        datetime(2026, 9, 13, 20, tzinfo=UTC),
        "Estadio del Horizonte",
        None,
    ),
    DemoFixture(
        UNION_TEAM_NAME,
        AWAY_TEAM_NAME,
        datetime(2026, 9, 14, 19, tzinfo=UTC),
        "Estadio del Valle",
        None,
    ),
)


def find_demo_match() -> Match | None:
    return Match.objects.filter(
        scheduled_at=SCHEDULED_AT,
        stadium_name=STADIUM_NAME,
        home_team_name=HOME_TEAM_NAME,
        away_team_name=AWAY_TEAM_NAME,
    ).first()


class Command(BaseCommand):
    help = "Crea cuatro equipos y diez partidos usando los casos de uso"

    @transaction.atomic
    def handle(self, *args, **options):
        self._resolve_use_cases()
        teams = {
            name: self._ensure_team(name, player_names)
            for name, player_names in TEAM_PLAYERS.items()
        }

        created = 0
        for fixture in FIXTURES:
            if self._fixture_exists(fixture, teams):
                continue
            self._create_fixture(fixture, teams)
            created += 1

        self.update_team.execute(
            team_id=teams[HOME_TEAM_NAME][0],
            name=HOME_TEAM_CURRENT_NAME,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Datos demo listos: 4 equipos, 10 partidos ({created} nuevos)")
        )

    def _resolve_use_cases(self) -> None:
        self.create_team = injector_instance.get(CreateTeamUseCase)
        self.register_squad = injector_instance.get(RegisterTeamSquadUseCase)
        self.create_match = injector_instance.get(CreateMatchUseCase)
        self.set_lineup = injector_instance.get(SetMatchLineupUseCase)
        self.start_match = injector_instance.get(StartMatchUseCase)
        self.register_goal = injector_instance.get(RegisterGoalUseCase)
        self.register_card = injector_instance.get(RegisterCardUseCase)
        self.disallow_goal = injector_instance.get(DisallowGoalUseCase)
        self.rescind_card = injector_instance.get(RescindCardUseCase)
        self.finish_match = injector_instance.get(FinishMatchUseCase)
        self.update_team = injector_instance.get(UpdateTeamUseCase)

    def _ensure_team(
        self,
        name: str,
        player_names: list[str],
    ) -> tuple[UUID, tuple[UUID, ...]]:
        aliases = [name]
        if name == HOME_TEAM_NAME:
            aliases.append(HOME_TEAM_CURRENT_NAME)
        team = Team.objects.filter(name__in=aliases).first()
        team_id = self.create_team.execute(name=name) if team is None else team.id

        existing_players = {
            player.name: player.id for player in Player.objects.filter(team_id=team_id)
        }
        if not existing_players:
            player_ids = self.register_squad.execute(
                team_id=team_id,
                player_names=player_names,
            )
        elif set(existing_players) == set(player_names):
            player_ids = tuple(existing_players[name] for name in player_names)
        else:
            raise CommandError(f"La plantilla demo de {name} está incompleta")
        return team_id, player_ids

    @staticmethod
    def _fixture_exists(fixture, teams) -> bool:
        return Match.objects.filter(
            home_team_id=teams[fixture.home][0],
            away_team_id=teams[fixture.away][0],
            scheduled_at=fixture.scheduled_at,
        ).exists()

    def _create_fixture(self, fixture: DemoFixture, teams) -> None:
        home_team_id, home_players = teams[fixture.home]
        away_team_id, away_players = teams[fixture.away]
        match_id = self.create_match.execute(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            scheduled_at=fixture.scheduled_at,
            stadium_name=fixture.stadium,
            referee_name="Alex Rivera",
        )
        self.set_lineup.execute(
            match_id=match_id,
            team_side=TeamSide.HOME,
            formation=MatchFormation.FOUR_THREE_THREE,
            players=self._lineup(home_players, captain_index=9),
        )
        self.set_lineup.execute(
            match_id=match_id,
            team_side=TeamSide.AWAY,
            formation=MatchFormation.FOUR_FOUR_TWO,
            players=self._lineup(away_players, captain_index=4),
        )
        if fixture.score is None:
            return

        self.start_match.execute(match_id, started_at=fixture.scheduled_at)
        for index in range(fixture.score[0]):
            self.register_goal.execute(
                match_id=match_id,
                player_id=home_players[(index + 8) % 11],
                minute=18 + index * 22,
            )
        for index in range(fixture.score[1]):
            self.register_goal.execute(
                match_id=match_id,
                player_id=away_players[(index + 9) % 11],
                minute=31 + index * 24,
            )
        if fixture.scheduled_at == SCHEDULED_AT:
            self._add_primary_match_events(match_id, home_players, away_players)
        self.finish_match.execute(
            match_id,
            finished_at=fixture.scheduled_at + timedelta(hours=1, minutes=52),
        )

    def _add_primary_match_events(self, match_id, home_players, away_players) -> None:
        disallowed_goal_id = self.register_goal.execute(
            match_id=match_id,
            player_id=away_players[7],
            minute=74,
        )
        self.disallow_goal.execute(match_id=match_id, goal_id=disallowed_goal_id)
        self.register_card.execute(
            match_id=match_id,
            player_id=home_players[3],
            card_type=CardType.YELLOW,
            minute=35,
        )
        self.register_card.execute(
            match_id=match_id,
            player_id=away_players[4],
            card_type=CardType.RED,
            minute=82,
        )
        rescinded_card_id = self.register_card.execute(
            match_id=match_id,
            player_id=away_players[2],
            card_type=CardType.YELLOW,
            minute=52,
        )
        self.rescind_card.execute(match_id=match_id, card_id=rescinded_card_id)

    @staticmethod
    def _lineup(player_ids, *, captain_index: int) -> list[LineupPlayerInput]:
        return [
            LineupPlayerInput(
                player_id=player_id,
                shirt_number=index,
                is_captain=index == captain_index,
            )
            for index, player_id in enumerate(player_ids, start=1)
        ]
