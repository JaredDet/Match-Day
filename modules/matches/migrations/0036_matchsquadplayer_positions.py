from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("matches", "0035_match_announced_added_minutes_match_clock_version_and_more")]
    operations = [
        migrations.AddField(model_name="matchsquadplayer", name="position_x", field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(model_name="matchsquadplayer", name="position_y", field=models.PositiveSmallIntegerField(blank=True, null=True)),
    ]
