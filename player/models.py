from django.db import models
from person.models import Person
from student.models import Student


class Player(models.Model):
	person = models.OneToOneField(
		Person,
		on_delete=models.CASCADE,
		primary_key=True,
		verbose_name="Player"
	)
	student = models.ForeignKey(
		Student,
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
		verbose_name="Student Information",
	)
	is_high_school_bowler = models.BooleanField(default=False)
	is_league_bowler = models.BooleanField(default=False)
	is_tournament_bowler = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["person__last_name", "person__first_name"]

	def __str__(self) -> str:
		return str(self.person)
