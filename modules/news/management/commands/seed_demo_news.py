from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.dependency_injector import injector_instance
from modules.matches.application.commands.create_match_use_case import CreateMatchUseCase
from modules.matches.application.commands.disallow_goal_use_case import DisallowGoalUseCase
from modules.matches.application.commands.end_match_period_use_case import EndMatchPeriodUseCase
from modules.matches.application.commands.finish_match_use_case import FinishMatchUseCase
from modules.matches.application.commands.finish_penalty_shootout_use_case import (
    FinishPenaltyShootoutUseCase,
)
from modules.matches.application.commands.reduce_penalty_shootout_participants_use_case import (
    ReducePenaltyShootoutParticipantsUseCase,
)
from modules.matches.application.commands.register_card_use_case import RegisterCardUseCase
from modules.matches.application.commands.register_corner_kick_use_case import (
    RegisterCornerKickUseCase,
)
from modules.matches.application.commands.register_foul_use_case import RegisterFoulUseCase
from modules.matches.application.commands.register_goal_use_case import RegisterGoalUseCase
from modules.matches.application.commands.register_injury_use_case import RegisterInjuryUseCase
from modules.matches.application.commands.register_offside_use_case import RegisterOffsideUseCase
from modules.matches.application.commands.register_penalty_attempt_use_case import (
    RegisterPenaltyAttemptUseCase,
)
from modules.matches.application.commands.register_penalty_shootout_kick_use_case import (
    RegisterPenaltyShootoutKickUseCase,
)
from modules.matches.application.commands.register_shot_use_case import RegisterShotUseCase
from modules.matches.application.commands.register_substitution_use_case import (
    RegisterSubstitutionUseCase,
)
from modules.matches.application.commands.register_var_review_use_case import (
    RegisterVarReviewUseCase,
)
from modules.matches.application.commands.rescind_card_use_case import RescindCardUseCase
from modules.matches.application.commands.set_match_lineup_use_case import (
    LineupPlayerInput,
    SetMatchLineupUseCase,
)
from modules.matches.application.commands.start_match_period_use_case import StartMatchPeriodUseCase
from modules.matches.application.commands.start_match_use_case import StartMatchUseCase
from modules.matches.application.commands.start_penalty_shootout_use_case import (
    StartPenaltyShootoutUseCase,
)
from modules.matches.application.commands.update_match_possession_use_case import (
    UpdateMatchPossessionUseCase,
)
from modules.matches.constants import MATCH_LINEUP_SIZE
from modules.matches.domain.card import CardType
from modules.matches.domain.goal import GoalType
from modules.matches.domain.match import Match, MatchFormation, MatchStatus
from modules.matches.domain.match_event import MatchPeriod, TeamSide
from modules.matches.domain.match_substitution import SubstitutionReason
from modules.matches.domain.penalty_attempt import PenaltyAttemptOutcome
from modules.matches.domain.penalty_shootout import (
    PenaltyKickOutcome,
    PenaltyShootoutDepartureReason,
    PenaltyShootoutIneligibilityReason,
)
from modules.matches.domain.shot import ShotOutcome
from modules.matches.domain.var_review import VarReviewDecision, VarReviewReason
from modules.news.application.commands.create_news_use_case import CreateNewsUseCase
from modules.news.application.commands.publish_news_use_case import PublishNewsUseCase
from modules.news.application.commands.schedule_news_use_case import ScheduleNewsUseCase
from modules.news.domain.news import News, NewsStatus
from modules.teams.application.commands.create_team_use_case import CreateTeamUseCase
from modules.teams.application.commands.register_player_use_case import RegisterPlayerUseCase
from modules.teams.application.commands.register_team_squad_use_case import (
    RegisterTeamSquadUseCase,
)
from modules.teams.application.commands.set_team_captain_use_case import (
    SetTeamCaptainUseCase,
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

TEAM_HEAD_COACHES = {
    HOME_TEAM_NAME: "Carlos Medina",
    AWAY_TEAM_NAME: "Rafael Contreras",
    UNION_TEAM_NAME: "Miguel Salinas",
    SPORTING_TEAM_NAME: "Fernando Lagos",
}

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
        "Elías Figueroa",
        "Álvaro Méndez",
        "Ramiro Quiroga",
        "Damián Ortiz",
        "Cristian Zamora",
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
        "Mauricio Riquelme",
        "Eduardo Villalobos",
        "Héctor Sepúlveda",
        "Germán Pino",
        "Ángel Saavedra",
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
        "Fernando Cáceres",
        "Ricardo Zambrano",
        "Baltazar Moya",
        "Claudio Farías",
        "Jonathan Toro",
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
        "Guillermo Sanhueza",
        "Ernesto Poblete",
        "Leandro Cifuentes",
        "Federico Yáñez",
        "Roberto Millán",
    ],
}


class DemoEventShowcase(StrEnum):
    OWN_GOAL_AND_ASSIST = "own_goal_and_assist"
    PENALTY_INJURY_VAR = "penalty_injury_var"


@dataclass(frozen=True, slots=True)
class DemoFixture:
    home: str
    away: str
    scheduled_at: datetime
    stadium: str
    score: tuple[int, int] | None
    target_period: MatchPeriod | None = None
    shootout_score: tuple[int, int] | None = None
    has_extra_time: bool = False
    event_showcase: DemoEventShowcase | None = None


@dataclass(frozen=True, slots=True)
class DemoNews:
    title: str
    content: dict
    team: str | None
    status: NewsStatus
    scheduled_at: datetime | None = None
    published_at: datetime | None = None


SHOOTOUT_FIXTURE = DemoFixture(
    UNION_TEAM_NAME,
    SPORTING_TEAM_NAME,
    datetime(2026, 7, 27, 18, tzinfo=UTC),
    "Estadio del Valle",
    (2, 2),
    shootout_score=(4, 3),
    has_extra_time=True,
)


FIXTURES = (
    DemoFixture(
        HOME_TEAM_NAME,
        SPORTING_TEAM_NAME,
        datetime(2026, 7, 13, 18, tzinfo=UTC),
        "Estadio del Horizonte",
        (2, 1),
        event_showcase=DemoEventShowcase.OWN_GOAL_AND_ASSIST,
    ),
    DemoFixture(
        AWAY_TEAM_NAME,
        UNION_TEAM_NAME,
        datetime(2026, 7, 16, 20, tzinfo=UTC),
        "Estadio Cordillera",
        (1, 0),
        event_showcase=DemoEventShowcase.PENALTY_INJURY_VAR,
    ),
    DemoFixture(
        AWAY_TEAM_NAME,
        HOME_TEAM_NAME,
        datetime(2026, 7, 20, 20, tzinfo=UTC),
        "Estadio Cordillera",
        (0, 1),
    ),
    SHOOTOUT_FIXTURE,
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
    DemoFixture(
        HOME_TEAM_NAME,
        AWAY_TEAM_NAME,
        SCHEDULED_AT,
        STADIUM_NAME,
        (2, 1),
    ),
    DemoFixture(
        HOME_TEAM_NAME,
        UNION_TEAM_NAME,
        datetime(2026, 8, 31, 15, tzinfo=UTC),
        "Estadio del Horizonte",
        (1, 0),
        MatchPeriod.FIRST_HALF,
    ),
    DemoFixture(
        AWAY_TEAM_NAME,
        SPORTING_TEAM_NAME,
        datetime(2026, 8, 31, 16, tzinfo=UTC),
        "Estadio Cordillera",
        (0, 1),
        MatchPeriod.HALFTIME,
    ),
    DemoFixture(
        UNION_TEAM_NAME,
        AWAY_TEAM_NAME,
        datetime(2026, 8, 31, 17, tzinfo=UTC),
        "Estadio del Valle",
        (1, 1),
        MatchPeriod.SECOND_HALF,
    ),
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


NEWS = (
    DemoNews(
        title="Atlético Bahía se prepara para una nueva jornada",
        content={
            "blocks": [
                {
                    "type": "paragraph",
                    "text": (
                        "Atlético Bahía continúa sus entrenamientos de cara a su "
                        "próximo compromiso de liga."
                    ),
                },
                {
                    "type": "paragraph",
                    "text": (
                        "El cuerpo técnico trabaja durante la semana para mantener "
                        "el buen momento del equipo."
                    ),
                },
            ]
        },
        team=HOME_TEAM_NAME,
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 5, 18, tzinfo=UTC),
    ),
    DemoNews(
        title="Deportivo Cordillera presenta su nueva plantilla",
        content={
            "blocks": [
                {
                    "type": "paragraph",
                    "text": (
                        "Deportivo Cordillera presentó oficialmente a los jugadores "
                        "que formarán parte de su plantilla esta temporada."
                    ),
                },
                {
                    "type": "paragraph",
                    "text": (
                        "El equipo comenzará su preparación con miras a los próximos "
                        "partidos del campeonato."
                    ),
                },
            ]
        },
        team=AWAY_TEAM_NAME,
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 8, 15, tzinfo=UTC),
    ),
    DemoNews(
        title="Unión del Valle anuncia su próximo partido",
        content={
            "blocks": [
                {
                    "type": "paragraph",
                    "text": (
                        "Unión del Valle ya tiene todo preparado para su próximo "
                        "partido como local."
                    ),
                },
            ]
        },
        team=UNION_TEAM_NAME,
        status=NewsStatus.SCHEDULED,
        scheduled_at=datetime(2026, 9, 25, 20, tzinfo=UTC),
    ),
    DemoNews(
        title="Sporting del Bosque prepara una jornada especial",
        content={
            "blocks": [
                {
                    "type": "paragraph",
                    "text": (
                        "El club prepara una jornada especial para sus hinchas "
                        "durante el próximo fin de semana."
                    ),
                },
            ]
        },
        team=SPORTING_TEAM_NAME,
        status=NewsStatus.SCHEDULED,
        scheduled_at=datetime(2026, 9, 27, 16, tzinfo=UTC),
    ),
    DemoNews(
        title="Resultados y novedades de la jornada",
        content={
            "blocks": [
                {
                    "type": "paragraph",
                    "text": (
                        "Revisa las principales novedades de la fecha y los resultados "
                        "de los encuentros disputados durante el fin de semana."
                    ),
                },
            ]
        },
        team=None,
        status=NewsStatus.PUBLISHED,
        published_at=datetime(2026, 8, 20, 12, tzinfo=UTC),
    ),
    DemoNews(
        title="Entrevista con el capitán de Atlético Bahía",
        content={
            "blocks": [
                {
                    "type": "paragraph",
                    "text": (
                        "El capitán de Atlético Bahía conversó sobre la preparación "
                        "del equipo y los objetivos para la temporada."
                    ),
                },
            ]
        },
        team=HOME_TEAM_NAME,
        status=NewsStatus.DRAFT,
    ),
    DemoNews(
        title="Información institucional del campeonato",
        content={
            "blocks": [
                {
                    "type": "paragraph",
                    "text": (
                        "La organización del campeonato informó novedades relacionadas "
                        "con la programación de las próximas jornadas."
                    ),
                },
            ]
        },
        team=None,
        status=NewsStatus.DRAFT,
    ),
)


def find_demo_match() -> Match | None:
    return Match.objects.filter(
        scheduled_at=SCHEDULED_AT,
        stadium_name=STADIUM_NAME,
        home_team_name=HOME_TEAM_NAME,
        away_team_name=AWAY_TEAM_NAME,
    ).first()


def find_demo_shootout_match() -> Match | None:
    return Match.objects.filter(
        penalty_shootout__isnull=False,
        scheduled_at=SHOOTOUT_FIXTURE.scheduled_at,
        stadium_name=SHOOTOUT_FIXTURE.stadium,
        home_team_name=SHOOTOUT_FIXTURE.home,
        away_team_name=SHOOTOUT_FIXTURE.away,
    ).first()


class Command(BaseCommand):
    help = "Crea cuatro equipos, quince partidos y noticias demo usando los casos de uso"

    @transaction.atomic
    def handle(self, *args, **options):
        self._resolve_use_cases()

        teams = {
            name: self._ensure_team(name, player_names)
            for name, player_names in TEAM_PLAYERS.items()
        }

        for team_id, player_ids in teams.values():
            self.set_team_captain.execute(
                team_id=team_id,
                player_id=player_ids[8],
            )

        self.update_team.execute(
            team_id=teams[HOME_TEAM_NAME][0],
            name=HOME_TEAM_NAME,
        )

        created = 0
        rebuilt = 0

        for fixture in FIXTURES:
            existing_match = self._find_fixture(fixture, teams)

            if existing_match is not None:
                if self._fixture_is_current(existing_match, fixture):
                    continue

                existing_match.substitutions.all().delete()
                existing_match.delete()
                rebuilt += 1
            else:
                created += 1

            self._create_fixture(fixture, teams)

        self.update_team.execute(
            team_id=teams[HOME_TEAM_NAME][0],
            name=HOME_TEAM_CURRENT_NAME,
        )

        news_created = self._seed_news(teams)

        self.stdout.write(
            self.style.SUCCESS(
                f"Datos demo listos: 4 equipos, {len(FIXTURES)} partidos "
                f"({created} nuevos, {rebuilt} reconstruidos), "
                f"{news_created} noticias nuevas"
            )
        )

    def _resolve_use_cases(self) -> None:
        self.create_team = injector_instance.get(CreateTeamUseCase)
        self.register_squad = injector_instance.get(RegisterTeamSquadUseCase)
        self.register_player = injector_instance.get(RegisterPlayerUseCase)
        self.set_team_captain = injector_instance.get(SetTeamCaptainUseCase)

        self.create_match = injector_instance.get(CreateMatchUseCase)
        self.set_lineup = injector_instance.get(SetMatchLineupUseCase)
        self.start_match = injector_instance.get(StartMatchUseCase)
        self.start_match_period = injector_instance.get(StartMatchPeriodUseCase)
        self.end_match_period = injector_instance.get(EndMatchPeriodUseCase)
        self.register_goal = injector_instance.get(RegisterGoalUseCase)
        self.register_foul = injector_instance.get(RegisterFoulUseCase)
        self.register_corner_kick = injector_instance.get(RegisterCornerKickUseCase)
        self.register_offside = injector_instance.get(RegisterOffsideUseCase)
        self.register_shot = injector_instance.get(RegisterShotUseCase)
        self.update_possession = injector_instance.get(UpdateMatchPossessionUseCase)
        self.register_penalty_attempt = injector_instance.get(RegisterPenaltyAttemptUseCase)
        self.register_injury = injector_instance.get(RegisterInjuryUseCase)
        self.register_var_review = injector_instance.get(RegisterVarReviewUseCase)
        self.register_card = injector_instance.get(RegisterCardUseCase)
        self.register_substitution = injector_instance.get(RegisterSubstitutionUseCase)
        self.disallow_goal = injector_instance.get(DisallowGoalUseCase)
        self.rescind_card = injector_instance.get(RescindCardUseCase)
        self.finish_match = injector_instance.get(FinishMatchUseCase)
        self.start_penalty_shootout = injector_instance.get(StartPenaltyShootoutUseCase)
        self.register_penalty_shootout_kick = injector_instance.get(
            RegisterPenaltyShootoutKickUseCase
        )
        self.reduce_penalty_shootout_participants = injector_instance.get(
            ReducePenaltyShootoutParticipantsUseCase
        )
        self.finish_penalty_shootout = injector_instance.get(FinishPenaltyShootoutUseCase)

        self.update_team = injector_instance.get(UpdateTeamUseCase)

        self.create_news = injector_instance.get(CreateNewsUseCase)
        self.schedule_news = injector_instance.get(ScheduleNewsUseCase)
        self.publish_news = injector_instance.get(PublishNewsUseCase)

    def _ensure_team(
        self,
        name: str,
        player_names: list[str],
    ) -> tuple[UUID, tuple[UUID, ...]]:
        aliases = [name]

        if name == HOME_TEAM_NAME:
            aliases.append(HOME_TEAM_CURRENT_NAME)

        team = Team.objects.filter(name__in=aliases).first()
        head_coach_name = TEAM_HEAD_COACHES[name]

        if team is None:
            team_id = self.create_team.execute(
                name=name,
                head_coach_name=head_coach_name,
            )
        else:
            team_id = team.id
            self.update_team.execute(
                team_id=team_id,
                head_coach_name=head_coach_name,
            )

        existing_players = {
            player.name: player.id for player in Player.objects.filter(team_id=team_id)
        }

        if not existing_players:
            player_ids = self.register_squad.execute(
                team_id=team_id,
                player_names=player_names,
            )
        else:
            unexpected_players = set(existing_players) - set(player_names)

            if unexpected_players:
                raise CommandError(f"La plantilla demo de {name} contiene jugadores inesperados")

            for player_name in player_names:
                if player_name not in existing_players:
                    existing_players[player_name] = self.register_player.execute(
                        team_id=team_id,
                        name=player_name,
                    )

            player_ids = tuple(existing_players[player_name] for player_name in player_names)

        return team_id, player_ids

    def _seed_news(self, teams) -> int:
        created = 0

        for news in NEWS:
            if News.objects.filter(title=news.title).exists():
                continue

            team_id = teams[news.team][0] if news.team is not None else None

            news_id = self.create_news.execute(
                title=news.title,
                content=news.content,
                team_id=team_id,
                cover_image=None,
            )

            if news.status == NewsStatus.SCHEDULED:
                if news.scheduled_at is None:
                    raise CommandError(f"La noticia demo '{news.title}' requiere scheduled_at")

                self.schedule_news.execute(
                    news_id=news_id,
                    scheduled_at=news.scheduled_at,
                )

            elif news.status == NewsStatus.PUBLISHED:
                self.publish_news.execute(
                    news_id=news_id,
                    published_at=news.published_at,
                )

            created += 1

        return created

    @staticmethod
    def _find_fixture(fixture, teams) -> Match | None:
        return Match.objects.filter(
            home_team_id=teams[fixture.home][0],
            away_team_id=teams[fixture.away][0],
            scheduled_at=fixture.scheduled_at,
        ).first()

    @staticmethod
    def _fixture_is_current(match: Match, fixture: DemoFixture) -> bool:
        expected_squad_size = len(TEAM_PLAYERS[fixture.home]) + len(TEAM_PLAYERS[fixture.away])

        if match.squad_players.count() != expected_squad_size:
            return False

        expected_sent_off_ids = set(
            match.cards.filter(
                card_type=CardType.RED,
                rescinded_at__isnull=True,
            ).values_list("player_id", flat=True)
        )

        actual_sent_off_ids = set(
            match.squad_players.filter(is_sent_off=True).values_list(
                "player_id",
                flat=True,
            )
        )

        if actual_sent_off_ids != expected_sent_off_ids:
            return False

        if fixture.score is None:
            expected_status = MatchStatus.SCHEDULED
            expected_period = None
            expected_minute = None
            expected_substitutions = 0
            expected_stat_events = 0
            expected_possession = None

        elif fixture.target_period is not None:
            expected_status = MatchStatus.LIVE
            expected_period = fixture.target_period
            expected_minute = {
                MatchPeriod.FIRST_HALF: 34,
                MatchPeriod.HALFTIME: 45,
                MatchPeriod.SECOND_HALF: 72,
            }[fixture.target_period]
            expected_substitutions = 2 if fixture.target_period == MatchPeriod.SECOND_HALF else 0
            expected_stat_events = 2 if fixture.target_period != MatchPeriod.SECOND_HALF else 3
            expected_possession = 50 + fixture.scheduled_at.day % 5

        else:
            expected_status = MatchStatus.FINISHED
            expected_period = (
                MatchPeriod.EXTRA_TIME_SECOND_HALF
                if fixture.has_extra_time
                else MatchPeriod.SECOND_HALF
            )
            expected_minute = 120 if fixture.has_extra_time else 90
            expected_substitutions = 2 + int(
                fixture.event_showcase == DemoEventShowcase.PENALTY_INJURY_VAR
            )
            expected_stat_events = 3
            expected_possession = 50 + fixture.scheduled_at.day % 5

        expected_shootout = fixture.shootout_score is not None
        expected_penalty_goals = int(fixture.scheduled_at == SCHEDULED_AT)
        expected_own_goals = int(fixture.event_showcase == DemoEventShowcase.OWN_GOAL_AND_ASSIST)
        expected_assisted_goals = expected_own_goals

        has_penalty_showcase = fixture.event_showcase == DemoEventShowcase.PENALTY_INJURY_VAR

        expected_penalty_attempts = int(has_penalty_showcase)
        expected_injuries = int(has_penalty_showcase)
        expected_var_reviews = int(has_penalty_showcase)

        shootout_is_current = not expected_shootout

        if expected_shootout and hasattr(match, "penalty_shootout"):
            shootout = match.penalty_shootout

            shootout_is_current = (
                (shootout.home_score, shootout.away_score) == fixture.shootout_score
                and shootout.home_kick_count == 5
                and shootout.away_kick_count == 5
                and shootout.kicks.count() == 10
                and set(
                    shootout.participants.filter(is_eligible=False).values_list(
                        "ineligibility_reason",
                        flat=True,
                    )
                )
                == {
                    PenaltyShootoutIneligibilityReason.INJURY,
                    PenaltyShootoutIneligibilityReason.OPPONENT_REDUCTION,
                }
            )

        clock = match.clock_snapshot()

        return (
            match.status == expected_status
            and (match.period_started_at is not None) == (fixture.score is not None)
            and (match.period_ended_at is not None)
            == (expected_status == MatchStatus.FINISHED or expected_period == MatchPeriod.HALFTIME)
            and match.home_head_coach_name == TEAM_HEAD_COACHES[fixture.home]
            and match.away_head_coach_name == TEAM_HEAD_COACHES[fixture.away]
            and match.current_period == expected_period
            and clock.minute == expected_minute
            and match.home_possession_percentage == expected_possession
            and match.shots.count() == expected_stat_events
            and match.fouls.count() == (0 if fixture.score is None else expected_stat_events - 1)
            and match.corner_kicks.count()
            == (0 if fixture.score is None else expected_stat_events - 1)
            and match.offsides.count() == (0 if fixture.score is None else expected_stat_events - 1)
            and match.substitutions.count() == expected_substitutions
            and hasattr(match, "penalty_shootout") == expected_shootout
            and shootout_is_current
            and match.goals.filter(
                goal_type=GoalType.PENALTY,
                disallowed_at__isnull=True,
            ).count()
            == expected_penalty_goals
            and match.goals.filter(
                goal_type=GoalType.OWN_GOAL,
                disallowed_at__isnull=True,
            ).count()
            == expected_own_goals
            and match.goals.filter(assist_player__isnull=False).count() == expected_assisted_goals
            and match.penalty_attempts.count() == expected_penalty_attempts
            and match.injuries.count() == expected_injuries
            and match.var_reviews.count() == expected_var_reviews
        )

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
            players=self._lineup(home_players),
            substitutes=self._substitutes(home_players),
        )

        self.set_lineup.execute(
            match_id=match_id,
            team_side=TeamSide.AWAY,
            formation=MatchFormation.FOUR_FOUR_TWO,
            players=self._lineup(away_players),
            substitutes=self._substitutes(away_players),
        )

        if fixture.score is None:
            return

        demo_now = timezone.now()

        if fixture.target_period == MatchPeriod.FIRST_HALF:
            first_half_started_at = demo_now - timedelta(
                minutes=34,
                seconds=30,
            )
        elif fixture.target_period == MatchPeriod.HALFTIME:
            first_half_started_at = demo_now - timedelta(minutes=46)
        elif fixture.target_period == MatchPeriod.SECOND_HALF:
            first_half_started_at = demo_now - timedelta(minutes=75)
        else:
            first_half_started_at = fixture.scheduled_at

        self.start_match.execute(
            match_id,
            started_at=first_half_started_at,
        )

        self.update_possession.execute(
            match_id=match_id,
            home_percentage=50 + fixture.scheduled_at.day % 5,
        )

        home_goals = [18 + index * 22 for index in range(fixture.score[0])]

        away_goals = [31 + index * 24 for index in range(fixture.score[1])]

        for index, minute in enumerate(home_goals):
            if minute > 45:
                continue

            is_showcase_own_goal = (
                fixture.event_showcase == DemoEventShowcase.OWN_GOAL_AND_ASSIST and index == 1
            )

            player_id = (
                away_players[4]
                if is_showcase_own_goal
                else home_players[(index + 8) % MATCH_LINEUP_SIZE]
            )

            goal_type = (
                GoalType.PENALTY
                if fixture.scheduled_at == SCHEDULED_AT and index == 0
                else GoalType.OWN_GOAL
                if is_showcase_own_goal
                else GoalType.REGULAR
            )

            self.register_goal.execute(
                match_id=match_id,
                player_id=player_id,
                minute=minute,
                goal_type=goal_type,
            )

        for index, minute in enumerate(away_goals):
            if minute > 45:
                continue

            assist_player_id = (
                away_players[(index + 8) % MATCH_LINEUP_SIZE]
                if (fixture.event_showcase == DemoEventShowcase.OWN_GOAL_AND_ASSIST and index == 0)
                else None
            )

            self.register_goal.execute(
                match_id=match_id,
                player_id=away_players[(index + 9) % MATCH_LINEUP_SIZE],
                assist_player_id=assist_player_id,
                minute=minute,
            )

        self._add_first_half_stat_events(
            match_id,
            home_players,
            away_players,
        )

        if fixture.target_period == MatchPeriod.FIRST_HALF:
            return

        if fixture.scheduled_at == SCHEDULED_AT:
            self.register_card.execute(
                match_id=match_id,
                player_id=home_players[3],
                card_type=CardType.YELLOW,
                minute=35,
            )

        first_half_ended_at = first_half_started_at + timedelta(minutes=45)

        self.end_match_period.execute(
            match_id,
            MatchPeriod.FIRST_HALF,
            ended_at=first_half_ended_at,
        )

        if fixture.target_period == MatchPeriod.HALFTIME:
            return

        second_half_started_at = (
            demo_now - timedelta(minutes=27, seconds=30)
            if fixture.target_period == MatchPeriod.SECOND_HALF
            else first_half_ended_at + timedelta(minutes=15)
        )

        self.start_match_period.execute(
            match_id,
            MatchPeriod.SECOND_HALF,
            started_at=second_half_started_at,
        )

        for index, minute in enumerate(home_goals):
            if minute <= 45:
                continue

            self.register_goal.execute(
                match_id=match_id,
                player_id=home_players[(index + 8) % MATCH_LINEUP_SIZE],
                minute=minute,
            )

        for index, minute in enumerate(away_goals):
            if minute <= 45:
                continue

            self.register_goal.execute(
                match_id=match_id,
                player_id=away_players[(index + 9) % MATCH_LINEUP_SIZE],
                minute=minute,
            )

        self._add_second_half_stat_events(
            match_id,
            home_players,
            away_players,
        )

        self.register_substitution.execute(
            match_id=match_id,
            player_out_id=home_players[1],
            player_in_id=home_players[MATCH_LINEUP_SIZE],
            minute=60,
        )

        self.register_substitution.execute(
            match_id=match_id,
            player_out_id=away_players[1],
            player_in_id=away_players[MATCH_LINEUP_SIZE],
            minute=65,
        )

        if fixture.target_period == MatchPeriod.SECOND_HALF:
            return

        if fixture.scheduled_at == SCHEDULED_AT:
            self._add_primary_match_events(
                match_id,
                home_players,
                away_players,
            )

        if fixture.event_showcase == DemoEventShowcase.PENALTY_INJURY_VAR:
            self._add_penalty_injury_var_events(
                match_id,
                home_players,
                away_players,
            )

        second_half_ended_at = second_half_started_at + timedelta(minutes=45)

        self.end_match_period.execute(
            match_id,
            MatchPeriod.SECOND_HALF,
            ended_at=second_half_ended_at,
        )

        finished_at = second_half_ended_at + timedelta(minutes=5)

        if fixture.has_extra_time:
            extra_time_first_half_started_at = second_half_ended_at + timedelta(minutes=5)

            self.start_match_period.execute(
                match_id,
                MatchPeriod.EXTRA_TIME_FIRST_HALF,
                started_at=extra_time_first_half_started_at,
            )

            extra_time_first_half_ended_at = extra_time_first_half_started_at + timedelta(
                minutes=15
            )

            self.end_match_period.execute(
                match_id,
                MatchPeriod.EXTRA_TIME_FIRST_HALF,
                ended_at=extra_time_first_half_ended_at,
            )

            extra_time_second_half_started_at = extra_time_first_half_ended_at + timedelta(
                minutes=5
            )

            self.start_match_period.execute(
                match_id,
                MatchPeriod.EXTRA_TIME_SECOND_HALF,
                started_at=extra_time_second_half_started_at,
            )

            extra_time_second_half_ended_at = extra_time_second_half_started_at + timedelta(
                minutes=15
            )

            self.end_match_period.execute(
                match_id,
                MatchPeriod.EXTRA_TIME_SECOND_HALF,
                ended_at=extra_time_second_half_ended_at,
            )

            finished_at = extra_time_second_half_ended_at + timedelta(minutes=5)

        if fixture.shootout_score is not None:
            self._add_penalty_shootout(
                match_id,
                home_players,
                away_players,
                fixture.shootout_score,
                finished_at,
            )
            return

        self.finish_match.execute(
            match_id,
            finished_at=finished_at,
        )

    def _add_penalty_shootout(
        self,
        match_id,
        home_players,
        away_players,
        score,
        finished_at,
    ) -> None:
        self.start_penalty_shootout.execute(
            match_id=match_id,
            starting_team_side=TeamSide.HOME,
        )

        for index in range(5):
            self.register_penalty_shootout_kick.execute(
                match_id=match_id,
                player_id=home_players[index + 2],
                outcome=(
                    PenaltyKickOutcome.SCORED if index < score[0] else PenaltyKickOutcome.MISSED
                ),
            )

            if index == 1:
                self.reduce_penalty_shootout_participants.execute(
                    match_id=match_id,
                    unavailable_player_id=home_players[10],
                    departure_reason=PenaltyShootoutDepartureReason.INJURY,
                    opponent_excluded_player_id=away_players[10],
                )

            self.register_penalty_shootout_kick.execute(
                match_id=match_id,
                player_id=away_players[index + 2],
                outcome=(
                    PenaltyKickOutcome.SCORED if index < score[1] else PenaltyKickOutcome.MISSED
                ),
            )

        self.finish_penalty_shootout.execute(
            match_id=match_id,
            finished_at=finished_at,
        )

    def _add_primary_match_events(
        self,
        match_id,
        home_players,
        away_players,
    ) -> None:
        disallowed_goal_id = self.register_goal.execute(
            match_id=match_id,
            player_id=away_players[7],
            minute=74,
        )

        self.disallow_goal.execute(
            match_id=match_id,
            goal_id=disallowed_goal_id,
        )

        self.register_card.execute(
            match_id=match_id,
            player_id=home_players[MATCH_LINEUP_SIZE],
            card_type=CardType.YELLOW,
            minute=68,
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

        self.rescind_card.execute(
            match_id=match_id,
            card_id=rescinded_card_id,
        )

    def _add_penalty_injury_var_events(
        self,
        match_id,
        home_players,
        away_players,
    ) -> None:
        self.register_injury.execute(
            match_id=match_id,
            player_id=away_players[5],
            minute=69,
        )

        penalty_attempt_id = self.register_penalty_attempt.execute(
            match_id=match_id,
            player_id=home_players[8],
            outcome=PenaltyAttemptOutcome.SAVED,
            minute=70,
        )

        self.register_var_review.execute(
            match_id=match_id,
            team_side=TeamSide.HOME,
            reason=VarReviewReason.PENALTY,
            decision=VarReviewDecision.CONFIRMED,
            reviewed_event_id=penalty_attempt_id,
            minute=71,
        )

        self.register_substitution.execute(
            match_id=match_id,
            player_out_id=away_players[5],
            player_in_id=away_players[MATCH_LINEUP_SIZE + 1],
            reason=SubstitutionReason.INJURY,
            minute=72,
        )

    def _add_first_half_stat_events(
        self,
        match_id,
        home_players,
        away_players,
    ) -> None:
        self.register_shot.execute(
            match_id=match_id,
            player_id=home_players[6],
            outcome=ShotOutcome.OFF_TARGET,
            minute=8,
        )

        self.register_foul.execute(
            match_id=match_id,
            player_id=away_players[6],
            minute=11,
        )

        self.register_corner_kick.execute(
            match_id=match_id,
            player_id=home_players[7],
            minute=14,
        )

        self.register_offside.execute(
            match_id=match_id,
            player_id=away_players[8],
            minute=22,
        )

        self.register_shot.execute(
            match_id=match_id,
            player_id=away_players[9],
            goalkeeper_id=home_players[0],
            outcome=ShotOutcome.SAVED,
            minute=26,
        )

    def _add_second_half_stat_events(
        self,
        match_id,
        home_players,
        away_players,
    ) -> None:
        self.register_foul.execute(
            match_id=match_id,
            player_id=home_players[3],
            minute=50,
        )

        self.register_corner_kick.execute(
            match_id=match_id,
            player_id=away_players[4],
            minute=55,
        )

        self.register_offside.execute(
            match_id=match_id,
            player_id=home_players[8],
            minute=58,
        )

        self.register_shot.execute(
            match_id=match_id,
            player_id=home_players[9],
            outcome=ShotOutcome.WOODWORK,
            minute=67,
        )

    @staticmethod
    def _lineup(player_ids) -> list[LineupPlayerInput]:
        return [
            LineupPlayerInput(
                player_id=player_id,
                shirt_number=index,
            )
            for index, player_id in enumerate(
                player_ids[:MATCH_LINEUP_SIZE],
                start=1,
            )
        ]

    @staticmethod
    def _substitutes(player_ids) -> list[LineupPlayerInput]:
        return [
            LineupPlayerInput(
                player_id=player_id,
                shirt_number=index,
            )
            for index, player_id in enumerate(
                player_ids[MATCH_LINEUP_SIZE:],
                start=MATCH_LINEUP_SIZE + 1,
            )
        ]
