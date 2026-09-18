from __future__ import annotations

import uuid
from datetime import datetime
from uuid import UUID

from django.db import models

from core.constants import NAME_MAX_LENGTH
from core.text import normalize_whitespace
from modules.news.errors import NewsErrors


class NewsStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SCHEDULED = "SCHEDULED", "Scheduled"
    PUBLISHED = "PUBLISHED", "Published"


class News(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    team = models.ForeignKey(
        "teams.Team",
        on_delete=models.PROTECT,
        related_name="news",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=NAME_MAX_LENGTH)

    cover_image = models.ImageField(upload_to="news/covers/", null=True, blank=True)
    content = models.JSONField(default=dict)

    status = models.CharField(
        max_length=20,
        choices=NewsStatus.choices,
        default=NewsStatus.DRAFT,
    )
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(
        cls,
        *,
        title: str,
        content: dict,
        team_id: UUID | None = None,
        cover_image: str | None = None,
    ) -> News:
        return cls(
            team_id=team_id,
            title=cls._normalize_title(title),
            cover_image=cover_image,
            content=content,
        )

    def rename(self, title: str) -> None:
        self._ensure_editable()
        self.title = self._normalize_title(title)

    def update_content(self, content: dict) -> None:
        self._ensure_editable()
        self.content = content

    def update_cover_image(self, cover_image: str | None) -> None:
        self._ensure_editable()
        self.cover_image = cover_image

    def schedule(self, scheduled_at: datetime) -> None:
        if self.status != NewsStatus.DRAFT:
            raise NewsErrors.CannotSchedule

        self.status = NewsStatus.SCHEDULED
        self.scheduled_at = scheduled_at

    def unschedule(self) -> None:
        if self.status != NewsStatus.SCHEDULED:
            raise NewsErrors.NotScheduled

        self.status = NewsStatus.DRAFT
        self.scheduled_at = None

    def publish(self, published_at: datetime) -> None:
        if self.status == NewsStatus.PUBLISHED:
            raise NewsErrors.AlreadyPublished

        self.status = NewsStatus.PUBLISHED
        self.published_at = published_at
        self.scheduled_at = None

    def _ensure_editable(self) -> None:
        if self.status == NewsStatus.PUBLISHED:
            raise NewsErrors.AlreadyPublished

    @staticmethod
    def _normalize_title(title: str) -> str:
        normalized_title = normalize_whitespace(title)
        if not normalized_title:
            raise NewsErrors.InvalidTitle
        return normalized_title

    @staticmethod
    def _normalize_title(title: str) -> str:
        normalized_title = normalize_whitespace(title)
        if not normalized_title:
            raise NewsErrors.InvalidTitle
        return normalized_title

    class Meta:
        db_table = "news"
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(title=""),
                name="news_title_not_empty",
            ),
        ]
