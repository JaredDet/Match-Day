from django.db import migrations, models

FIRST_HALF = "first_half"
SECOND_HALF = "second_half"


def populate_official_time(apps, schema_editor):
    Match = apps.get_model("matches", "Match")
    Goal = apps.get_model("matches", "Goal")
    Card = apps.get_model("matches", "Card")
    MatchSubstitution = apps.get_model("matches", "MatchSubstitution")

    Match.objects.filter(status="live").update(current_period=FIRST_HALF)
    Match.objects.filter(status="finished").update(current_period=SECOND_HALF)

    for model in (Goal, Card, MatchSubstitution):
        model.objects.filter(minute__lte=45).update(period=FIRST_HALF)
        model.objects.filter(minute__gt=45).update(period=SECOND_HALF)
        for event in model.objects.filter(minute__gt=90).iterator():
            event.added_minute = event.minute - 90
            event.minute = 90
            event.save(update_fields=("minute", "added_minute"))


class Migration(migrations.Migration):
    dependencies = [("matches", "0019_matchsquadplayer_is_on_field_matchsubstitution")]

    operations = [
        migrations.RemoveConstraint(
            model_name="match",
            name="valid_match_lifecycle_timestamps",
        ),
        migrations.RemoveConstraint(model_name="goal", name="valid_goal_minute"),
        migrations.RemoveConstraint(model_name="card", name="valid_card_minute"),
        migrations.RemoveConstraint(
            model_name="matchsubstitution",
            name="valid_substitution_minute",
        ),
        migrations.AddField(
            model_name="match",
            name="current_period",
            field=models.CharField(
                blank=True,
                choices=[
                    ("first_half", "First Half"),
                    ("halftime", "Halftime"),
                    ("second_half", "Second Half"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        *[
            migrations.AddField(
                model_name=model_name,
                name="period",
                field=models.CharField(
                    choices=[
                        ("first_half", "First Half"),
                        ("halftime", "Halftime"),
                        ("second_half", "Second Half"),
                    ],
                    max_length=20,
                    null=True,
                ),
            )
            for model_name in ("goal", "card", "matchsubstitution")
        ],
        *[
            migrations.AddField(
                model_name=model_name,
                name="added_minute",
                field=models.PositiveSmallIntegerField(default=0),
            )
            for model_name in ("goal", "card", "matchsubstitution")
        ],
        migrations.RunPython(populate_official_time, migrations.RunPython.noop),
        *[
            migrations.AlterField(
                model_name=model_name,
                name="period",
                field=models.CharField(
                    choices=[
                        ("first_half", "First Half"),
                        ("halftime", "Halftime"),
                        ("second_half", "Second Half"),
                    ],
                    max_length=20,
                ),
            )
            for model_name in ("goal", "card", "matchsubstitution")
        ],
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                condition=models.Q(current_period__isnull=True)
                | models.Q(current_period__in=["first_half", "halftime", "second_half"]),
                name="valid_match_period",
            ),
        ),
        migrations.AddConstraint(
            model_name="match",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        status="scheduled",
                        current_period__isnull=True,
                        started_at__isnull=True,
                        finished_at__isnull=True,
                    )
                    | models.Q(
                        status="live",
                        current_period__in=["first_half", "halftime", "second_half"],
                        started_at__isnull=False,
                        finished_at__isnull=True,
                    )
                    | models.Q(
                        status="finished",
                        current_period="second_half",
                        started_at__isnull=False,
                        finished_at__isnull=False,
                    )
                ),
                name="valid_match_lifecycle_timestamps",
            ),
        ),
        *[
            migrations.AddConstraint(
                model_name=model_name,
                constraint=models.CheckConstraint(
                    condition=models.Q(minute__gte=1, minute__lte=90),
                    name=f"valid_{prefix}_minute",
                ),
            )
            for model_name, prefix in (
                ("goal", "goal"),
                ("card", "card"),
                ("matchsubstitution", "substitution"),
            )
        ],
        *[
            migrations.AddConstraint(
                model_name=model_name,
                constraint=models.CheckConstraint(
                    condition=(
                        models.Q(period="first_half", minute__gte=1, minute__lte=45)
                        | models.Q(period="second_half", minute__gte=46, minute__lte=90)
                    ),
                    name=f"valid_{prefix}_period_minute",
                ),
            )
            for model_name, prefix in (
                ("goal", "goal"),
                ("card", "card"),
                ("matchsubstitution", "substitution"),
            )
        ],
        *[
            migrations.AddConstraint(
                model_name=model_name,
                constraint=models.CheckConstraint(
                    condition=(
                        models.Q(added_minute=0)
                        | models.Q(period="first_half", minute=45)
                        | models.Q(period="second_half", minute=90)
                    ),
                    name=f"valid_{prefix}_added_minute",
                ),
            )
            for model_name, prefix in (
                ("goal", "goal"),
                ("card", "card"),
                ("matchsubstitution", "substitution"),
            )
        ],
    ]
