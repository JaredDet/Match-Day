from dataclasses import dataclass
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from core.demo_images import demo_image
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

TEAM_PROFILES = {
    HOME_TEAM_NAME: ("Valparaíso", "Estadio del Horizonte", 1932),
    AWAY_TEAM_NAME: ("Rancagua", "Estadio Cordillera", 1940),
    UNION_TEAM_NAME: ("Talca", "Estadio del Valle", 1937),
    SPORTING_TEAM_NAME: ("Temuco", "Parque del Bosque", 1950),
}


@dataclass(frozen=True, slots=True)
class DemoNews:
    title: str
    content: dict
    team: str | None
    status: NewsStatus
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    preview: str = ""


NEWS = (
    DemoNews(
        title="Atlético Bahía se prepara para una nueva jornada",
        content={
            "children": [
                "<h1>Atlético Bahía afina los últimos detalles</h1>",
                "Atlético Bahía continúa sus entrenamientos de cara a su "
                "próximo compromiso de liga.",
                "<h2>Trabajo con la pelota</h2>",
                "El cuerpo técnico trabaja durante la semana para mantener "
                "el <b>buen momento del equipo</b>.",
                "La preparación combina ejercicios tácticos y recuperación física.",
                "<h3>Un plan para los noventa minutos</h3>",
                "Durante la semana, el cuerpo técnico revisa videos del rival y ensaya distintas salidas desde el fondo. Los laterales alternan proyecciones, mientras los mediocampistas trabajan la presión tras pérdida y la circulación rápida.",
                "<h4>La voz del vestuario</h4>",
                "El plantel llega motivado y sabe que el apoyo de su gente será importante. La convocatoria se confirmará después del último entrenamiento.",
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
                "<h1>El plantel para la nueva temporada</h1>",
                "Deportivo Cordillera presentó oficialmente a los jugadores "
                "que formarán parte de su plantilla esta temporada.",
                "<h2>Un grupo listo para competir</h2>",
                "El equipo comenzará su preparación con miras a los próximos "
                "partidos del <i>campeonato</i>.",
                "<h3>Integración de los juveniles</h3>",
                "Varios jugadores formados en casa se sumaron a las prácticas del primer equipo. El cuerpo técnico seguirá de cerca su adaptación y espera que aporten energía y alternativas durante una temporada exigente.",
                "<h4>Próximos pasos</h4>",
                "La planificación contempla amistosos, sesiones de análisis y trabajo específico por puesto antes del debut oficial.",
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
                "<h1>El próximo desafío en casa</h1>",
                "Unión del Valle ya tiene todo preparado para su próximo partido como local.",
                "<h2>Una jornada especial para la hinchada</h2>",
                "El encuentro será una jornada <b><i>especial</i></b> para sus hinchas.",
                "<h3>Detalles del encuentro</h3>",
                "El equipo utilizará la semana para ajustar la pelota detenida y mejorar la coordinación entre sus líneas. En casa buscará imponer el ritmo desde el comienzo y aprovechar los espacios que deje el rival.",
                "<h4>Entradas y acceso</h4>",
                "El club publicará los horarios de apertura y la información de entradas en sus canales oficiales antes del fin de semana.",
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
                "<h1>El club prepara una jornada para su gente</h1>",
                "El club prepara una jornada especial para sus hinchas "
                "durante el próximo fin de semana.",
                "<h2>Actividades antes del partido</h2>",
                "La programación incluirá encuentros con el plantel y actividades para familias.",
                "<h3>Una tarde para compartir</h3>",
                "La jornada comenzará con actividades para niños y continuará con música y espacios de encuentro en las inmediaciones del estadio. La organización recomienda llegar con anticipación para facilitar el ingreso.",
                "<h4>Información para asistentes</h4>",
                "Los detalles de acceso y los horarios definitivos se comunicarán durante los próximos días.",
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
                "<h1>Lo que dejó la fecha</h1>",
                "Revisa las principales novedades de la fecha y los resultados "
                "de los encuentros disputados durante el fin de semana.",
                "<h2>Resultados destacados</h2>",
                "Consulta los <b>resultados destacados</b> y las novedades de cada encuentro.",
                "<h3>Lo que viene</h3>",
                "Los equipos ya preparan sus próximos compromisos.",
                "<h4>La tabla empieza a tomar forma</h4>",
                "La diferencia de goles puede ser decisiva cuando varios clubes terminan igualados en puntos. Por eso, cada gol anotado y cada ocasión defendida cuentan en la carrera por avanzar.",
                "En la próxima fecha habrá enfrentamientos directos entre equipos que luchan por los primeros puestos. Sigue el calendario para revisar horarios, resultados y cambios en la clasificación.",
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
                "<h1>Una conversación sobre el equipo</h1>",
                "El capitán de Atlético Bahía conversó sobre la preparación "
                "del equipo y los objetivos para la temporada.",
                "<h2>La importancia del grupo</h2>",
                "El jugador destacó la importancia de mantener el <i>trabajo colectivo</i>.",
                "<h3>Un objetivo compartido</h3>",
                "En la conversación también habló sobre la relación con los hinchas, la responsabilidad de representar al club y la importancia de mantener la calma en los momentos difíciles de un partido.",
                "<h4>Preparación para el próximo desafío</h4>",
                "El capitán espera que el equipo mantenga la intensidad de los entrenamientos y convierta ese trabajo en una actuación sólida el fin de semana.",
            ]
        },
        team=HOME_TEAM_NAME,
        status=NewsStatus.DRAFT,
    ),
    DemoNews(
        title="Información institucional del campeonato",
        content={
            "children": [
                "<h1>Novedades del campeonato</h1>",
                "La organización del campeonato informó novedades relacionadas "
                "con la programación de las próximas jornadas.",
                "<h2>Programación</h2>",
                "Los clubes recibirán el calendario actualizado durante los próximos días.",
                "<h3>Coordinación con los clubes</h3>",
                "La organización trabaja con los equipos y los recintos para confirmar horarios que faciliten los traslados y la asistencia del público. Los cambios se comunicarán oportunamente en el calendario oficial.",
                "<h4>Canales oficiales</h4>",
                "Las bases, fechas y avisos importantes estarán disponibles en Matchday para que clubes e hinchas consulten una fuente única de información.",
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
        updated = 0

        for item in NEWS:
            existing_news = News.objects.filter(title=item.title).first()
            if existing_news:
                if existing_news.content != item.content or existing_news.preview != item.preview:
                    # This command owns demo content and must refresh it even after publication.
                    News.objects.filter(pk=existing_news.pk).update(
                        content=item.content, preview=item.preview
                    )
                    updated += 1
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
                        city=TEAM_PROFILES[item.team][0],
                        stadium_name=TEAM_PROFILES[item.team][1],
                        founded_year=TEAM_PROFILES[item.team][2],
                    )
                )

            cover = demo_image(
                title=item.title,
                colors=("#173520", "#789c48") if team_id else ("#2b3150", "#7f69a8"),
                size=(1280, 720),
            )
            cover.name = f"{item.title.lower().replace(' ', '-')[:60]}.webp"
            news_id = create_news.execute(
                title=item.title,
                content=item.content,
                preview=item.preview,
                team_id=team_id,
                cover_image=cover,
            )

            if item.status == NewsStatus.SCHEDULED:
                schedule_news.execute(news_id=news_id, scheduled_at=item.scheduled_at)
            elif item.status == NewsStatus.PUBLISHED:
                publish_news.execute(news_id=news_id, published_at=item.published_at)

            created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Noticias demo listas: {created} nuevas, {updated} actualizadas")
        )
