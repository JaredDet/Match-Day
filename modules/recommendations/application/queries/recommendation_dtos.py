from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from modules.recommendations.domain.content_reference import ContentKind


@dataclass(frozen=True, slots=True)
class RecommendationItem:
    kind: ContentKind
    id: UUID
    title: str
    endpoint: str
    preview: str
    score: float
    reason: str


@dataclass(frozen=True, slots=True)
class RecommendationFeed:
    personalized: bool
    generated_at: datetime | None
    expires_at: datetime | None
    news: tuple[RecommendationItem, ...]
    matches: tuple[RecommendationItem, ...]
    tournaments: tuple[RecommendationItem, ...]
    discovery: tuple[RecommendationItem, ...]


@dataclass(frozen=True, slots=True)
class RecommendationSnapshotDetail:
    sections: dict
    generated_at: datetime
    expires_at: datetime
