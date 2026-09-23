from dataclasses import dataclass
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.dependency_injector import injector_instance
from modules.news.application.commands.create_news_use_case import CreateNewsUseCase
from modules.news.application.commands.publish_news_use_case import PublishNewsUseCase
from modules.news.application.commands.schedule_news_use_case import ScheduleNewsUseCase
from modules.news.domain.news import News, NewsStatus
from modules.teams.application.commands.create_team_use_case import CreateTeamUseCase
from modules.teams.domain.team import Team

HOME_TEAM_NAME = "Atlético del Puerto"


HOME_TEAM_CURRENT_NAME = "Atlético Bahía"


AWAY_TEAM_NAME = "Deportivo Cordillera"


UNION_TEAM_NAME = "Unión del Valle"


SPORTING_TEAM_NAME = "Sporting del Bosque"


DEMO_REFERENCE = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)


TEAM_HEAD_COACHES = {
    HOME_TEAM_NAME: "Carlos Medina",
    AWAY_TEAM_NAME: "Rafael Contreras",
    UNION_TEAM_NAME: "Miguel Salinas",
    SPORTING_TEAM_NAME: "Fernando Lagos",
}


@dataclass(frozen=True, slots=True)
class DemoNews:
    title: str
    content: dict
    team: str | None
    status: NewsStatus
    scheduled_at: datetime | None = None
    published_at: datetime | None = None


NEWS = (
    DemoNews(
        title="Atlético Bahía se prepara para una nueva jornada",
        content={
            "children": [
                "Atlético Bahía continúa sus entrenamientos de cara a su "
                "próximo compromiso de liga.",
                "El cuerpo técnico trabaja durante la semana para mantener "
                "el <b>buen momento del equipo</b>.",
            ]
        },
        team=HOME_TEAM_NAME,
        status=NewsStatus.PUBLISHED,
        published_at=DEMO_REFERENCE - timedelta(days=14),
    ),
    DemoNews(
        title="Deportivo Cordillera presenta su nueva plantilla",
        content={
            "children": [
                "Deportivo Cordillera presentó oficialmente a los jugadores "
                "que formarán parte de su plantilla esta temporada.",
                "El equipo comenzará su preparación con miras a los próximos "
                "partidos del <i>campeonato</i>.",
            ]
        },
        team=AWAY_TEAM_NAME,
        status=NewsStatus.PUBLISHED,
        published_at=DEMO_REFERENCE - timedelta(days=10),
    ),
    DemoNews(
        title="Unión del Valle anuncia su próximo partido",
        content={
            "children": [
                "Unión del Valle ya tiene todo preparado para su próximo partido como local.",
                "El encuentro será una jornada <b><i>especial</i></b> para sus hinchas.",
            ]
        },
        team=UNION_TEAM_NAME,
        status=NewsStatus.SCHEDULED,
        scheduled_at=DEMO_REFERENCE + timedelta(days=2, hours=8),
    ),
    DemoNews(
        title="Sporting del Bosque prepara una jornada especial",
        content={
            "children": [
                "El club prepara una jornada especial para sus hinchas "
                "durante el próximo fin de semana.",
            ]
        },
        team=SPORTING_TEAM_NAME,
        status=NewsStatus.SCHEDULED,
        scheduled_at=DEMO_REFERENCE + timedelta(days=4, hours=4),
    ),
    DemoNews(
        title="Resultados y novedades de la jornada",
        content={
            "children": [
                "Revisa las principales novedades de la fecha y los resultados "
                "de los encuentros disputados durante el fin de semana.",
                "Consulta los <b>resultados destacados</b> y las novedades de cada encuentro.",
            ]
        },
        team=None,
        status=NewsStatus.PUBLISHED,
        published_at=DEMO_REFERENCE - timedelta(days=3),
    ),
    DemoNews(
        title="Entrevista con el capitán de Atlético Bahía",
        content={
            "children": [
                "El capitán de Atlético Bahía conversó sobre la preparación "
                "del equipo y los objetivos para la temporada.",
                "El jugador destacó la importancia de mantener el <i>trabajo colectivo</i>.",
            ]
        },
        team=HOME_TEAM_NAME,
        status=NewsStatus.DRAFT,
    ),
    DemoNews(
        title="Información institucional del campeonato",
        content={
            "children": [
                "La organización del campeonato informó novedades relacionadas "
                "con la programación de las próximas jornadas.",
            ]
        },
        team=None,
        status=NewsStatus.DRAFT,
    ),
)


class Command(BaseCommand):
    help = "Crea siete noticias demo y los equipos asociados que falten"

    @transaction.atomic
    def handle(self, *args, **options):
        create_news = injector_instance.get(CreateNewsUseCase)
        schedule_news = injector_instance.get(ScheduleNewsUseCase)
        publish_news = injector_instance.get(PublishNewsUseCase)
        create_team = injector_instance.get(CreateTeamUseCase)
        created = 0

        for item in NEWS:
            if News.objects.filter(title=item.title).exists():
                continue

            team_id = None

            if item.team is not None:
                aliases = [item.team]
                name = item.team

                if name == HOME_TEAM_NAME:
                    aliases.append(HOME_TEAM_CURRENT_NAME)
                    name = HOME_TEAM_CURRENT_NAME

                team = Team.objects.filter(name__in=aliases).first()
                team_id = (
                    team.id
                    if team
                    else create_team.execute(
                        name=name,
                        head_coach_name=TEAM_HEAD_COACHES[item.team],
                    )
                )

            news_id = create_news.execute(title=item.title, content=item.content, team_id=team_id)

            if item.status == NewsStatus.SCHEDULED:
                schedule_news.execute(news_id=news_id, scheduled_at=item.scheduled_at)
            elif item.status == NewsStatus.PUBLISHED:
                publish_news.execute(news_id=news_id, published_at=item.published_at)

            created += 1

        self.stdout.write(self.style.SUCCESS(f"Noticias demo listas: {created} nuevas"))
