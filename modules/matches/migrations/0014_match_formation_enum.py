from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("matches", "0013_match_lineup")]

    operations = [
        migrations.AlterField(
            model_name="matchlineup",
            name="formation",
            field=models.CharField(
                choices=[
                    ("4-3-3", "4-3-3"),
                    ("4-4-2", "4-4-2"),
                    ("4-2-3-1", "4-2-3-1"),
                    ("4-1-4-1", "4-1-4-1"),
                    ("3-5-2", "3-5-2"),
                    ("3-4-3", "3-4-3"),
                ],
                max_length=20,
            ),
        ),
        migrations.AddConstraint(
            model_name="matchlineup",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    formation__in=[
                        "4-3-3",
                        "4-4-2",
                        "4-2-3-1",
                        "4-1-4-1",
                        "3-5-2",
                        "3-4-3",
                    ]
                ),
                name="valid_match_formation",
            ),
        ),
    ]
