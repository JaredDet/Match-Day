from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from django.db import models


class ContentKind(models.TextChoices):
    TEAM = "team"
    PLAYER = "player"
    NEWS = "news"
    MATCH = "match"
    TOURNAMENT = "tournament"


@dataclass(frozen=True, slots=True)
class ContentReference:
    kind: ContentKind
    id: UUID

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.id}"


@dataclass(frozen=True, slots=True)
class RecommendationContent:
    reference: ContentReference
    title: str
    endpoint: str
    preview: str
    team_ids: tuple[UUID, ...] = ()
    tournament_ids: tuple[UUID, ...] = ()
    date: datetime | None = None
    live: bool = False
    image: str | None = None
