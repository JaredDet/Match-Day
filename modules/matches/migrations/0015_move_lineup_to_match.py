from django.db import migrations, models

FORMATIONS = ["4-3-3", "4-4-2", "4-2-3-1", "4-1-4-1", "3-5-2", "3-4-3"]
FORMATION_CHOICES = [(formation, formation) for formation in FORMATIONS]


def move_lineups_to_matches(apps, schema_editor):
    Match = apps.get_model("matches", "Match")
    MatchLineup = apps.get_model("matches", "MatchLineup")

    for lineup in MatchLineup.objects.iterator():
        field = f"{lineup.team_side}_formation"
        Match.objects.filter(pk=lineup.match_id).update(**{field: lineup.formation})


class Migration(migrations.Migration):
    dependencies = [("matches", "0014_match_formation_enum")]

    operations = [
        migrations.AddField(
            model_name="match",
            name="home_formation",
            field=models.CharField(
                blank=True,
                choices=FORMATION_CHOICES,
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="match",
            name="away_formation",
            field=models.CharField(
                blank=True,
                choices=FORMATION_CHOICES,
                max_length=20,
                null=True,
            ),
        ),
        migrations.RunPython(move_lineups_to_matches, migrations.RunPython.noop),
        migrations.DeleteModel(name="MatchLineup"),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(home_formation__isnull=True) | models.Q(home_formation__in=FORMATIONS)
                ),
                name="valid_home_match_formation",
            ),
        ),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(away_formation__isnull=True) | models.Q(away_formation__in=FORMATIONS)
                ),
                name="valid_away_match_formation",
            ),
        ),
    ]
