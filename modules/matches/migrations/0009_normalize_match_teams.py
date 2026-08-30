import hashlib
import uuid
from datetime import UTC

import django.db.models.deletion
from django.db import migrations, models


def populate_teams(apps, schema_editor):
    match_model = apps.get_model("matches", "Match")
    team_model = apps.get_model("teams", "Team")
    teams_by_name = {}

    for match in match_model.objects.all().iterator():
        resolved_teams = []
        for name in (match.home_team_name, match.away_team_name):
            normalized_name = " ".join(name.split())
            key = normalized_name.casefold()
            team = teams_by_name.get(key)
            if team is None:
                team = team_model.objects.filter(name__iexact=normalized_name).first()
            if team is None:
                team = team_model.objects.create(id=uuid.uuid4(), name=normalized_name)
            teams_by_name[key] = team
            resolved_teams.append(team)

        match.home_team_id = resolved_teams[0].id
        match.away_team_id = resolved_teams[1].id
        team_ids = sorted((str(match.home_team_id), str(match.away_team_id)))
        instant = match.scheduled_at.astimezone(UTC).isoformat()
        payload = f"{team_ids[0]}\0{team_ids[1]}\0{instant}"
        match.fixture_key = hashlib.sha256(payload.encode()).hexdigest()
        match.save(update_fields=["home_team", "away_team", "fixture_key"])


class Migration(migrations.Migration):
    dependencies = [
        ("matches", "0008_rename_event_status_fields"),
        ("teams", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="match",
            name="match_team_names_not_empty",
        ),
        migrations.RemoveConstraint(
            model_name="match",
            name="match_teams_are_different",
        ),
        migrations.AddField(
            model_name="match",
            name="away_team",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="away_matches",
                to="teams.team",
            ),
        ),
        migrations.AddField(
            model_name="match",
            name="home_team",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="home_matches",
                to="teams.team",
            ),
        ),
        migrations.RunPython(populate_teams, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="match",
            name="away_team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="away_matches",
                to="teams.team",
            ),
        ),
        migrations.AlterField(
            model_name="match",
            name="home_team",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="home_matches",
                to="teams.team",
            ),
        ),
        migrations.RemoveField(model_name="match", name="away_team_name"),
        migrations.RemoveField(model_name="match", name="home_team_name"),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                condition=~models.Q(home_team=models.F("away_team")),
                name="match_teams_are_different",
            ),
        ),
    ]
