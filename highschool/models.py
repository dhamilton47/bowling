from django.db import models

from address.models import Address


class HighSchool(models.Model):
	school_name = models.CharField(max_length=100)
	school_mascot = models.CharField(
		max_length=100,
		blank=True,
		null=True
	)
	address = models.ForeignKey(
		Address,
		on_delete=models.DO_NOTHING,
		blank=True,
		null=True,
		related_name="high_schools",
		verbose_name="High School Address",
	)

	class Meta:
		verbose_name = "High School"
		verbose_name_plural = "High Schools"
		ordering = ["school_name"]

	def __str__(self) -> str:
		return str(self.school_name)
