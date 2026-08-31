import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("matches", "0017_matchlineupplayer_role_and_more")]

    operations = [
        migrations.RemoveConstraint(
            model_name="matchlineupplayer",
            name="unique_player_per_match_lineup",
        ),
        migrations.RemoveConstraint(
            model_name="matchlineupplayer",
            name="unique_shirt_per_match_team",
        ),
        migrations.RemoveConstraint(
            model_name="matchlineupplayer",
            name="unique_captain_per_match_team",
        ),
        migrations.RemoveConstraint(
            model_name="matchlineupplayer",
            name="valid_lineup_player_team_side",
        ),
        migrations.RemoveConstraint(
            model_name="matchlineupplayer",
            name="valid_lineup_shirt_number",
        ),
        migrations.RenameModel(
            old_name="MatchLineupPlayer",
            new_name="MatchSquadPlayer",
        ),
        migrations.AlterModelTable(
            name="matchsquadplayer",
            table="match_squad_players",
        ),
        migrations.AlterField(
            model_name="matchsquadplayer",
            name="match",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="squad_players",
                to="matches.match",
            ),
        ),
        migrations.AlterField(
            model_name="matchsquadplayer",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="match_squads",
                to="teams.player",
            ),
        ),
        migrations.AddConstraint(
            model_name="matchsquadplayer",
            constraint=models.UniqueConstraint(
                fields=("match", "player"),
                name="unique_player_per_match_squad",
            ),
        ),
        migrations.AddConstraint(
            model_name="matchsquadplayer",
            constraint=models.UniqueConstraint(
                fields=("match", "team_side", "shirt_number"),
                name="unique_squad_shirt_per_match_team",
            ),
        ),
        migrations.AddConstraint(
            model_name="matchsquadplayer",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_captain", True)),
                fields=("match", "team_side"),
                name="unique_squad_captain_per_match_team",
            ),
        ),
        migrations.AddConstraint(
            model_name="matchsquadplayer",
            constraint=models.CheckConstraint(
                condition=models.Q(("team_side__in", ["home", "away"])),
                name="valid_squad_player_team_side",
            ),
        ),
        migrations.AddConstraint(
            model_name="matchsquadplayer",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("shirt_number__gte", 1),
                    ("shirt_number__lte", 99),
                ),
                name="valid_squad_shirt_number",
            ),
        ),
    ]
