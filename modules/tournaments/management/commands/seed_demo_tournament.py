from datetime import date
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from core.demo_images import demo_image
from core.dependency_injector import injector_instance
from modules.matches.domain.match import Match, MatchStatus
from modules.teams.application.commands.update_team_use_case import UpdateTeamUseCase
from modules.teams.domain.team import Team
from modules.tournaments.application.commands.create_fixture_use_case import CreateFixtureUseCase
from modules.tournaments.application.commands.create_group_entry_use_case import (
    CreateGroupEntryUseCase,
)
from modules.tournaments.application.commands.create_group_use_case import CreateGroupUseCase
from modules.tournaments.application.commands.create_phase_use_case import CreatePhaseUseCase
from modules.tournaments.application.commands.create_season_use_case import CreateSeasonUseCase
from modules.tournaments.application.commands.create_tournament_use_case import (
    CreateTournamentUseCase,
)
from modules.tournaments.application.commands.set_phase_status_use_case import (
    SetPhaseStatusUseCase,
)
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.group import Group
from modules.tournaments.domain.group_entry import GroupEntry
from modules.tournaments.domain.phase import Phase, PhaseKind, PhaseStatus
from modules.tournaments.domain.season import Season
from modules.tournaments.domain.tournament import Tournament

TOURNAMENT_SLUG = "copa-matchday"
TEAM_COLORS = (
    ("#58427c", "#8e79b8"),
    ("#164f3d", "#4d8a70"),
    ("#315b91", "#7096c9"),
    ("#76542a", "#b68a52"),
)


class Command(BaseCommand):
    help = "Crea un torneo demo completo con temporada, grupos y eliminatorias"

    @transaction.atomic
    def handle(self, *args, **options):
        if not Tournament.objects.filter(slug=TOURNAMENT_SLUG).exists():
            call_command("seed_demo_match", stdout=StringIO())
        teams = tuple(Team.objects.order_by("name")[:4])
        self._ensure_team_crests(teams)
        tournament = self._ensure_tournament()
        season = self._ensure_season(tournament, teams)
        group_phase = self._ensure_phase(season, "Fase de grupos", PhaseKind.GROUPS, 1, 4, 6)
        group = self._ensure_group(group_phase)
        for team in teams:
            if not GroupEntry.objects.filter(group=group, team=team).exists():
                injector_instance.get(CreateGroupEntryUseCase).execute(
                    group_id=group.id, team_id=team.id
                )

        finished = tuple(Match.objects.filter(status=MatchStatus.FINISHED).order_by("scheduled_at"))
        live = Match.objects.filter(status=MatchStatus.LIVE).order_by("scheduled_at").first()
        scheduled = (
            Match.objects.filter(status=MatchStatus.SCHEDULED).order_by("scheduled_at").first()
        )
        self._ensure_fixtures(group_phase, finished[:6], group=group)
        self._set_status(group_phase, PhaseStatus.FINISHED)

        semifinals = self._ensure_phase(season, "Semifinales", PhaseKind.KNOCKOUT, 2, 2, 1)
        self._ensure_fixtures(semifinals, finished[6:8])
        self._set_status(semifinals, PhaseStatus.FINISHED)

        final = self._ensure_phase(season, "Final", PhaseKind.KNOCKOUT, 3, 1, 1)
        if live:
            self._ensure_fixtures(final, (live,))
        self._set_status(final, PhaseStatus.LIVE)

        third = self._ensure_phase(season, "Tercer puesto", PhaseKind.THIRD_PLACE, 4, 0, 1)
        if scheduled:
            self._ensure_fixtures(third, (scheduled,))

        self.stdout.write(self.style.SUCCESS("Torneo demo listo: Copa Matchday"))

    @staticmethod
    def _ensure_team_crests(teams):
        update = injector_instance.get(UpdateTeamUseCase)
        for team, colors in zip(teams, TEAM_COLORS, strict=True):
            if team.crest:
                continue
            crest = demo_image(title=team.name, colors=colors, size=(320, 320))
            crest.name = f"{team.name.lower().replace(' ', '-')}.webp"
            update.execute(team_id=team.id, crest=crest)

    @staticmethod
    def _ensure_tournament():
        tournament = Tournament.objects.filter(slug=TOURNAMENT_SLUG).first()
        if tournament:
            return tournament
        logo = demo_image(title="Copa Matchday", colors=("#193d23", "#9acb55"), size=(480, 480))
        logo.name = "copa-matchday.webp"
        tournament_id = injector_instance.get(CreateTournamentUseCase).execute(
            slug=TOURNAMENT_SLUG,
            name="Copa Matchday",
            country="Chile",
            category="Copa nacional",
            logo=logo,
            max_teams_per_group=4,
        )
        return Tournament.objects.get(id=tournament_id)

    @staticmethod
    def _ensure_season(tournament, teams):
        name = str(date.today().year)
        season = Season.objects.filter(tournament=tournament, name=name).first()
        if season:
            return season
        season_id = injector_instance.get(CreateSeasonUseCase).execute(
            tournament_id=tournament.id,
            name=name,
            team_ids=[team.id for team in teams],
        )
        return Season.objects.get(id=season_id)

    @staticmethod
    def _ensure_phase(season, name, kind, order, qualifying, matchdays):
        phase = Phase.objects.filter(season=season, order=order).first()
        if phase:
            return phase
        phase_id = injector_instance.get(CreatePhaseUseCase).execute(
            season_id=season.id,
            name=name,
            kind=kind,
            order=order,
            qualifying_teams=qualifying,
            matchdays=matchdays,
        )
        return Phase.objects.get(id=phase_id)

    @staticmethod
    def _ensure_group(phase):
        group = Group.objects.filter(phase=phase, name="A").first()
        if group:
            return group
        group_id = injector_instance.get(CreateGroupUseCase).execute(phase_id=phase.id, name="A")
        return Group.objects.get(id=group_id)

    @staticmethod
    def _ensure_fixtures(phase, matches, group=None):
        create = injector_instance.get(CreateFixtureUseCase)
        for position, match in enumerate(matches, 1):
            if Fixture.objects.filter(match=match).exists():
                continue
            create.execute(
                phase_id=phase.id,
                group_id=group.id if group else None,
                match_id=match.id,
                position=position,
                matchday=min(position, phase.matchdays),
            )

    @staticmethod
    def _set_status(phase, status):
        if phase.status == status:
            return
        injector_instance.get(SetPhaseStatusUseCase).execute(phase_id=phase.id, status=status)
