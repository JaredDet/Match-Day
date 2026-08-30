from datetime import UTC, datetime, timedelta

from django.core.management.base import BaseCommand
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

SCHEDULED_AT = datetime(2026, 8, 30, 20, tzinfo=UTC)
STADIUM_NAME = "Estadio del Horizonte"
HOME_TEAM_NAME = "Atlético del Puerto"
AWAY_TEAM_NAME = "Deportivo Cordillera"
HOME_PLAYER_NAMES = [
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
]
AWAY_PLAYER_NAMES = [
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
]


def find_demo_match() -> Match | None:
    return Match.objects.filter(
        scheduled_at=SCHEDULED_AT,
        stadium_name=STADIUM_NAME,
        home_team_name=HOME_TEAM_NAME,
        away_team_name=AWAY_TEAM_NAME,
    ).first()


class Command(BaseCommand):
    help = "Crea un partido finalizado usando los casos de uso de la V2"

    @transaction.atomic
    def handle(self, *args, **options):
        existing_match = find_demo_match()
        if existing_match is not None:
            self.stdout.write(
                self.style.WARNING(f"El partido de demostración ya existe: {existing_match.id}")
            )
            return

        create_team = injector_instance.get(CreateTeamUseCase)
        register_squad = injector_instance.get(RegisterTeamSquadUseCase)
        create_match = injector_instance.get(CreateMatchUseCase)
        set_lineup = injector_instance.get(SetMatchLineupUseCase)
        start_match = injector_instance.get(StartMatchUseCase)
        register_goal = injector_instance.get(RegisterGoalUseCase)
        register_card = injector_instance.get(RegisterCardUseCase)
        disallow_goal = injector_instance.get(DisallowGoalUseCase)
        rescind_card = injector_instance.get(RescindCardUseCase)
        finish_match = injector_instance.get(FinishMatchUseCase)
        update_team = injector_instance.get(UpdateTeamUseCase)

        home_team_id = create_team.execute(name=HOME_TEAM_NAME)
        away_team_id = create_team.execute(name=AWAY_TEAM_NAME)
        home_player_ids = register_squad.execute(
            team_id=home_team_id,
            player_names=HOME_PLAYER_NAMES,
        )
        away_player_ids = register_squad.execute(
            team_id=away_team_id,
            player_names=AWAY_PLAYER_NAMES,
        )
        match_id = create_match.execute(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            scheduled_at=SCHEDULED_AT,
            stadium_name=STADIUM_NAME,
            referee_name="Alex Rivera",
        )
        set_lineup.execute(
            match_id=match_id,
            team_side=TeamSide.HOME,
            formation=MatchFormation.FOUR_THREE_THREE,
            players=self._lineup(home_player_ids, captain_index=9),
        )
        set_lineup.execute(
            match_id=match_id,
            team_side=TeamSide.AWAY,
            formation=MatchFormation.FOUR_FOUR_TWO,
            players=self._lineup(away_player_ids, captain_index=4),
        )
        start_match.execute(match_id, started_at=SCHEDULED_AT)

        register_goal.execute(match_id=match_id, player_id=home_player_ids[8], minute=18)
        register_goal.execute(match_id=match_id, player_id=away_player_ids[9], minute=41)
        register_goal.execute(match_id=match_id, player_id=home_player_ids[10], minute=67)
        disallowed_goal_id = register_goal.execute(
            match_id=match_id,
            player_id=away_player_ids[7],
            minute=74,
        )
        disallow_goal.execute(match_id=match_id, goal_id=disallowed_goal_id)

        register_card.execute(
            match_id=match_id,
            player_id=home_player_ids[3],
            card_type=CardType.YELLOW,
            minute=35,
        )
        register_card.execute(
            match_id=match_id,
            player_id=away_player_ids[4],
            card_type=CardType.RED,
            minute=82,
        )
        rescinded_card_id = register_card.execute(
            match_id=match_id,
            player_id=away_player_ids[2],
            card_type=CardType.YELLOW,
            minute=52,
        )
        rescind_card.execute(match_id=match_id, card_id=rescinded_card_id)
        finish_match.execute(
            match_id,
            finished_at=SCHEDULED_AT + timedelta(hours=1, minutes=52),
        )
        update_team.execute(team_id=home_team_id, name="Atlético Bahía")

        self.stdout.write(self.style.SUCCESS(f"Partido de demostración creado: {match_id}"))

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
