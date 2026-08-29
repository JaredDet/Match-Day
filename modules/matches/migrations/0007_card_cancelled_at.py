from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("matches", "0006_goal_cancelled_at")]

    operations = [
        migrations.AddField(
            model_name="card",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
