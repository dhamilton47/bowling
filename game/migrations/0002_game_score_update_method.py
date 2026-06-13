from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("game", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="game",
            name="score_update_method",
            field=models.CharField(
                choices=[
                    ("each_ball", "Update after each ball"),
                    (
                        "defer_after_triple_strike",
                        "Update after each ball until three strikes, then at end of strike streak",
                    ),
                ],
                default="each_ball",
                max_length=32,
            ),
        ),
    ]
