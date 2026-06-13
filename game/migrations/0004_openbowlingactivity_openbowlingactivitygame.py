from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("player", "0004_alter_player_student"),
        ("game", "0003_alter_frame_ball1_alter_frame_ball2_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="OpenBowlingActivity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="Open Bowling", max_length=100)),
                ("sequence_number", models.PositiveIntegerField(default=1)),
                ("is_complete", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-sequence_number", "-created_at"]},
        ),
        migrations.CreateModel(
            name="OpenBowlingActivityGame",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.PositiveIntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "activity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activity_games",
                        to="game.openbowlingactivity",
                    ),
                ),
                (
                    "game",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="open_bowling_entry",
                        to="game.game",
                    ),
                ),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="open_bowling_games",
                        to="player.player",
                    ),
                ),
            ],
            options={"ordering": ["sort_order", "id"]},
        ),
        migrations.AddConstraint(
            model_name="openbowlingactivitygame",
            constraint=models.UniqueConstraint(
                fields=("activity", "player"),
                name="open_bowling_unique_player_per_activity",
            ),
        ),
        migrations.AddConstraint(
            model_name="openbowlingactivitygame",
            constraint=models.UniqueConstraint(
                fields=("activity", "sort_order"),
                name="open_bowling_unique_sort_order_per_activity",
            ),
        ),
    ]
