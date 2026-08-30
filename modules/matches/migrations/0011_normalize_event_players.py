import uuid

import django.db.models.deletion
from django.db import migrations, models


def populate_event_players(apps, schema_editor):
    goal_model = apps.get_model("matches", "Goal")
    card_model = apps.get_model("matches", "Card")
    player_model = apps.get_model("teams", "Player")
    players_by_team_and_name = {}

    for event_model in (goal_model, card_model):
        events = event_model.objects.select_related("match").all().iterator()
        for event in events:
            team_id = (
                event.match.home_team_id if event.team_side == "home" else event.match.away_team_id
            )
            normalized_name = " ".join(event.player_name.split())
            key = (team_id, normalized_name.casefold())
            player = players_by_team_and_name.get(key)
            if player is None:
                player = player_model.objects.filter(
                    team_id=team_id,
                    name__iexact=normalized_name,
                ).first()
            if player is None:
                player = player_model.objects.create(
                    id=uuid.uuid4(),
                    team_id=team_id,
                    name=normalized_name,
                )
            players_by_team_and_name[key] = player
            event.player_id = player.id
            event.save(update_fields=["player"])


class Migration(migrations.Migration):
    dependencies = [
        ("matches", "0010_match_team_name_snapshots"),
        ("teams", "0002_player"),
    ]

    operations = [
        migrations.AddField(
            model_name="goal",
            name="player",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="goals",
                to="teams.player",
            ),
        ),
        migrations.AddField(
            model_name="card",
            name="player",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cards",
                to="teams.player",
            ),
        ),
        migrations.RunPython(populate_event_players, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="goal",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="goals",
                to="teams.player",
            ),
        ),
        migrations.AlterField(
            model_name="card",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cards",
                to="teams.player",
            ),
        ),
    ]
