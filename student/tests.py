from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction

from highschool.models import HighSchool
from student.models import Student


class StudentModelTests(TestCase):
	def setUp(self):
		self.high_school = HighSchool.objects.create(school_name="Westlake High School")

	def test_has_one_to_one_relation_to_high_school(self):
		field = Student._meta.get_field("high_school")
		self.assertIsInstance(field, models.OneToOneField)
		self.assertEqual(field.related_model, HighSchool)
		self.assertTrue(field.primary_key)
		self.assertIs(field.remote_field.on_delete, models.DO_NOTHING)
		self.assertEqual(field.verbose_name, "High School")

	def test_year_in_school_has_built_in_choices(self):
		field = Student._meta.get_field("year_in_school")
		self.assertTrue(field.choices)

		labels = {str(label).strip().lower() for _, label in field.choices}
		self.assertIn("freshman", labels)
		self.assertIn("sophomore", labels)
		self.assertIn("junior", labels)
		self.assertIn("senior", labels)

	def test_can_create_student_with_valid_year_choice(self):
		field = Student._meta.get_field("year_in_school")
		valid_value = next(value for value, _ in field.choices)

		student = Student.objects.create(
			high_school=self.high_school,
			year_in_school=valid_value,
		)

		self.assertEqual(student.high_school, self.high_school)
		self.assertEqual(student.year_in_school, valid_value)

	def test_year_in_school_has_default_value(self):
		student = Student.objects.create(high_school=self.high_school)
		self.assertEqual(student.year_in_school, Student.YearInSchool.FRESHMAN)

	def test_invalid_year_choice_fails_validation(self):
		student = Student(
			high_school=self.high_school,
			year_in_school="NOT_A_VALID_YEAR",
		)

		with self.assertRaises(ValidationError):
			student.full_clean()

	def test_high_school_relation_is_unique(self):
		field = Student._meta.get_field("year_in_school")
		valid_value = next(value for value, _ in field.choices)

		Student.objects.create(high_school=self.high_school, year_in_school=valid_value)

		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				Student.objects.create(high_school=self.high_school, year_in_school=valid_value)

	def test_created_and_updated_timestamp_fields_exist(self):
		created_field = Student._meta.get_field("created_at")
		updated_field = Student._meta.get_field("updated_at")

		self.assertIsInstance(created_field, models.DateTimeField)
		self.assertIsInstance(updated_field, models.DateTimeField)
		self.assertTrue(created_field.auto_now_add)
		self.assertTrue(updated_field.auto_now)
