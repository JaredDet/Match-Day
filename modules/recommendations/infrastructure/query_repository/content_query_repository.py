from collections import defaultdict

from django.db.models import Q
from django.urls import reverse

from modules.matches.domain.match import Match, MatchStatus
from modules.news.domain.news import News, NewsStatus
from modules.news.domain.news_preview import news_preview
from modules.recommendations.constants import CANDIDATES_PER_KIND
from modules.recommendations.domain.content_reference import (
    ContentKind,
    ContentReference,
    RecommendationContent,
)
from modules.teams.domain.player import Player
from modules.teams.domain.team import Team
from modules.tournaments.domain.fixture import Fixture
from modules.tournaments.domain.season import Season
from modules.tournaments.domain.tournament import Tournament


class ContentQueryRepository:
    def resolve(self, references):
        ids = defaultdict(set)
        for reference in references:
            ids[reference.kind].add(reference.id)
        teams = list(Team.objects.filter(id__in=ids[ContentKind.TEAM]))
        players = list(Player.objects.filter(id__in=ids[ContentKind.PLAYER]))
        news = list(News.objects.filter(id__in=ids[ContentKind.NEWS], status=NewsStatus.PUBLISHED))
        matches = list(Match.objects.filter(id__in=ids[ContentKind.MATCH]))
        tournaments = list(Tournament.objects.filter(id__in=ids[ContentKind.TOURNAMENT]))
        team_ids = {team.id for team in teams} | {player.team_id for player in players}
        team_ids.update(item.team_id for item in news if item.team_id)
        memberships = defaultdict(set)
        for team_id, tournament_id in Season.teams.through.objects.filter(
            team_id__in=team_ids
        ).values_list("team_id", "season__tournament_id"):
            memberships[team_id].add(tournament_id)
        match_tournaments = dict(
            Fixture.objects.filter(match_id__in=[match.id for match in matches]).values_list(
                "match_id", "phase__season__tournament_id"
            )
        )
        contents = []
        for team in teams:
            contents.append(
                RecommendationContent(
                    ContentReference(ContentKind.TEAM, team.id),
                    team.name,
                    reverse("teams-detail", args=[team.id]),
                    "",
                    (team.id,),
                    tuple(sorted(memberships[team.id])),
                )
            )
        for player in players:
            contents.append(
                RecommendationContent(
                    ContentReference(ContentKind.PLAYER, player.id),
                    player.name,
                    reverse("players-detail", args=[player.id]),
                    "",
                    (player.team_id,),
                    tuple(sorted(memberships[player.team_id])),
                )
            )
        for item in news:
            contents.append(
                RecommendationContent(
                    ContentReference(ContentKind.NEWS, item.id),
                    item.title,
                    reverse("news-detail", args=[item.id]),
                    news_preview(item.content),
                    (item.team_id,) if item.team_id else (),
                    tuple(sorted(memberships[item.team_id])) if item.team_id else (),
                    item.published_at,
                )
            )
        for match in matches:
            tournament_id = match_tournaments.get(match.id)
            contents.append(
                RecommendationContent(
                    ContentReference(ContentKind.MATCH, match.id),
                    f"{match.home_team_name} - {match.away_team_name}",
                    reverse("matches-detail", args=[match.id]),
                    "",
                    (match.home_team_id, match.away_team_id),
                    (tournament_id,) if tournament_id else (),
                    match.scheduled_at,
                    match.status == MatchStatus.LIVE,
                )
            )
        for tournament in tournaments:
            contents.append(
                RecommendationContent(
                    ContentReference(ContentKind.TOURNAMENT, tournament.id),
                    tournament.name,
                    reverse("tournaments-detail", args=[tournament.slug]),
                    "",
                    (),
                    (tournament.id,),
                )
            )
        return {content.reference.key: content for content in contents}

    def exists(self, reference):
        return reference.key in self.resolve([reference])

    def candidates(self, profile, now):
        limit = CANDIDATES_PER_KIND
        references = set()

        def include(kind, queryset):
            references.update(
                ContentReference(kind, id) for id in queryset.values_list("id", flat=True)[:limit]
            )

        preferred_teams = sorted(profile.teams, key=profile.teams.get, reverse=True)[:20]
        preferred_tournaments = sorted(
            profile.tournaments, key=profile.tournaments.get, reverse=True
        )[:20]
        include(ContentKind.TEAM, Team.objects.order_by("name", "id"))
        include(ContentKind.TEAM, Team.objects.filter(id__in=preferred_teams))
        public_news = News.objects.filter(status=NewsStatus.PUBLISHED).order_by(
            "-published_at", "id"
        )
        include(ContentKind.NEWS, public_news)
        include(
            ContentKind.NEWS,
            public_news.filter(
                Q(team_id__in=preferred_teams)
                | Q(team__tournament_seasons__tournament_id__in=preferred_tournaments)
            ).distinct(),
        )
        include(
            ContentKind.MATCH,
            Match.objects.filter(status=MatchStatus.LIVE).order_by("scheduled_at", "id"),
        )
        include(
            ContentKind.MATCH,
            Match.objects.filter(status=MatchStatus.SCHEDULED, scheduled_at__gte=now).order_by(
                "scheduled_at", "id"
            ),
        )
        include(
            ContentKind.MATCH,
            Match.objects.filter(status=MatchStatus.FINISHED, scheduled_at__lte=now).order_by(
                "-scheduled_at", "id"
            ),
        )
        include(
            ContentKind.MATCH,
            Match.objects.filter(
                Q(home_team_id__in=preferred_teams)
                | Q(away_team_id__in=preferred_teams)
                | Q(tournament_fixture__phase__season__tournament_id__in=preferred_tournaments)
            ).order_by("-scheduled_at", "id"),
        )
        include(ContentKind.TOURNAMENT, Tournament.objects.order_by("name", "id"))
        include(ContentKind.TOURNAMENT, Tournament.objects.filter(id__in=preferred_tournaments))
        return tuple(self.resolve(references).values())
