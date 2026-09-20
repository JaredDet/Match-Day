from django.apps import AppConfig


class TournamentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.tournaments"
    label = "tournaments"

    def ready(self):
        from modules.tournaments.infrastructure import match_completion  # noqa: F401
