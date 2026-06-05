from django.db import models

from highschool.models import HighSchool


class Student(models.Model):
	class YearInSchool(models.TextChoices):
		FRESHMAN = "FR", "Freshman"
		SOPHOMORE = "SO", "Sophomore"
		JUNIOR = "JR", "Junior"
		SENIOR = "SR", "Senior"

	high_school = models.OneToOneField(
		HighSchool,
		on_delete=models.DO_NOTHING,
		primary_key=True,
		verbose_name="High School",
	)
	year_in_school = models.CharField(
		max_length=2,
		choices=YearInSchool.choices,
		default=YearInSchool.FRESHMAN,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["high_school__school_name"]
		verbose_name = "Student"

	def __str__(self) -> str:
		return str(self.high_school.school_name)
