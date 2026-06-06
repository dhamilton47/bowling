from django.db import models
from player.models import Player


class Team(models.Model):
	team = models.CharField(
		max_length=100,
		blank=True,
		null=True
	)
	players = models.ManyToManyField(
		Player,
		blank=True,
		verbose_name="Players"
	)

	class Meta:
		ordering = ["team"]

	def __str__(self) -> str:
		return str(self.team)
