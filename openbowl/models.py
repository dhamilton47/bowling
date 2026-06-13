from django.db import models

from game.models import Game
from player.models import Player


class OpenBowlingActivity(models.Model):
    name = models.CharField(max_length=100, default="Open Bowling")
    sequence_number = models.PositiveIntegerField(default=1)
    is_complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-sequence_number", "-created_at"]
        db_table = "game_openbowlingactivity"

    def __str__(self):
        return f"{self.name} #{self.sequence_number}"


class OpenBowlingActivityGame(models.Model):
    activity = models.ForeignKey(
        OpenBowlingActivity,
        on_delete=models.CASCADE,
        related_name="activity_games",
    )
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="open_bowling_games",
    )
    game = models.OneToOneField(
        Game,
        on_delete=models.CASCADE,
        related_name="open_bowling_entry",
    )
    sort_order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        db_table = "game_openbowlingactivitygame"
        constraints = [
            models.UniqueConstraint(
                fields=["activity", "player"],
                name="open_bowling_unique_player_per_activity",
            ),
            models.UniqueConstraint(
                fields=["activity", "sort_order"],
                name="open_bowling_unique_sort_order_per_activity",
            ),
        ]

    def __str__(self):
        return f"{self.activity} - {self.player}"
