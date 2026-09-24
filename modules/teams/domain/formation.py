import uuid

from django.db import models

from core.text import normalize_whitespace
from modules.teams.errors import TeamErrors

FORMATION_CHOICES = [
    (value, value) for value in ("4-3-3", "4-4-2", "4-2-3-1", "4-1-4-1", "3-5-2", "3-4-3")
]


class TeamFormation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey("teams.Team", on_delete=models.CASCADE, related_name="formations")
    name = models.CharField(max_length=80)
    shape = models.CharField(max_length=10, choices=FORMATION_CHOICES)
    positions = models.JSONField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, *, team, name: str, shape: str, positions: list[dict], is_default=False):
        formation = cls(team=team)
        formation.update(name=name, shape=shape, positions=positions, is_default=is_default)
        return formation

    def update(self, *, name: str, shape: str, positions: list[dict], is_default=False):
        self.name = normalize_whitespace(name)
        if not self.name:
            raise TeamErrors.InvalidFormation
        if shape not in dict(FORMATION_CHOICES):
            raise TeamErrors.InvalidFormation
        self.shape = shape
        self.positions = self._validate_positions(positions)
        self.is_default = is_default

    @staticmethod
    def _validate_positions(positions: list[dict]) -> list[dict]:
        if len(positions) != 11:
            raise TeamErrors.InvalidFormation
        slots = set()
        normalized = []
        for position in positions:
            slot, x, y = position.get("slot"), position.get("x"), position.get("y")
            if not isinstance(slot, int) or isinstance(slot, bool) or slot < 1 or slot > 11:
                raise TeamErrors.InvalidFormation
            if slot in slots or not all(
                isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 100
                for value in (x, y)
            ):
                raise TeamErrors.InvalidFormation
            slots.add(slot)
            normalized.append({"slot": slot, "x": x, "y": y})
        return sorted(normalized, key=lambda item: item["slot"])

    class Meta:
        db_table = "team_formations"
        ordering = ["name", "id"]
        constraints = [
            models.UniqueConstraint(fields=["team", "name"], name="unique_team_formation_name"),
            models.UniqueConstraint(
                fields=["team"],
                condition=models.Q(is_default=True),
                name="unique_default_formation_per_team",
            ),
        ]
