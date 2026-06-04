from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from address.models import Address


class Person(models.Model):
	address = models.ForeignKey(
		Address,
		on_delete=models.PROTECT,
		related_name="people",
		blank=True,
		null=True,
	)
	first_name = models.CharField(
		max_length=30,
		blank=True,
		null=True
	)
	middle_name = models.CharField(
		max_length=30,
		blank=True,
		null=True
	)
	last_name = models.CharField(
		max_length=50,
		blank=True,
		null=True
	)
	preferred_name = models.CharField(
		max_length=30,
		blank=True,
		null=True
	)
	suffix = models.CharField(
		max_length=20,
		blank=True,
		default=""
	) # e.g. Jr., II, III
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = "Person"
		verbose_name_plural = "People"
		ordering = ["last_name", "first_name", "middle_name"]
		constraints = [
			# Prevent empty-string first_name/last_name at DB level.
			# Violating this will raise a DB IntegrityError on save().
			models.CheckConstraint(
				condition=~Q(first_name="") & ~Q(last_name=""),
				name="person_first_last_not_empty_str",
			),
			models.UniqueConstraint(
				fields=["first_name", "last_name", "address", "suffix"],
				condition=~Q(suffix="") & Q(suffix__isnull=False),
				name="person_name_address_suffix_unique_when_suffix_present",
			),
		]

	def clean(self):
		super().clean()

		if not self.first_name or not self.last_name or not self.address_id:
			return

		matching_people = Person.objects.filter(
			first_name=self.first_name,
			last_name=self.last_name,
			address_id=self.address_id,
		).exclude(pk=self.pk)

		if not matching_people.exists():
			return

		current_suffix = (self.suffix or "").strip()
		if not current_suffix:
			raise ValidationError(
				"Duplicate first_name, last_name, and address requires a non-empty suffix."
			)

		if matching_people.filter(Q(suffix="") | Q(suffix__isnull=True)).exists():
			raise ValidationError(
				"Duplicate first_name, last_name, and address is allowed only when all records have non-empty suffixes."
			)

		if matching_people.filter(suffix=current_suffix).exists():
			raise ValidationError(
				"Suffix must be unique for duplicate first_name, last_name, and address records."
			)

	def save(self, *args, **kwargs):
		self.full_clean(validate_constraints=False)
		return super().save(*args, **kwargs)

	def __str__(self) -> str:
		name = f"{self.first_name}"
		if self.middle_name:
			name += f" {self.middle_name}"
		name += f" {self.last_name}"
		if self.suffix:
			name += f", {self.suffix}"
		return name.strip()
