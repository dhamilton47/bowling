from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("openbowl", "0001_initial"),
        ("game", "0004_openbowlingactivity_openbowlingactivitygame"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name="OpenBowlingActivityGame"),
                migrations.DeleteModel(name="OpenBowlingActivity"),
            ],
        )
    ]
