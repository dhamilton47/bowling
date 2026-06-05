from django.test import TestCase
from django.db import models
from django.db import IntegrityError
from django.db import transaction
from address.models import Address, City, State

from .models import HighSchool


class HighSchoolModelTests(TestCase):
	def setUp(self):
		self.state = State.objects.create(state="Texas", state_abbr="TX")
		self.city = City.objects.create(city="Austin", state=self.state, zip_code="78701")
		self.address = Address.objects.create(street1="100 School Way", city=self.city)

	def test_can_create_high_school_with_required_fields(self):
		school = HighSchool.objects.create(
			school_name="Westlake High School",
			school_mascot="Chaparrals",
			address=self.address,
		)

		self.assertEqual(school.school_name, "Westlake High School")
		self.assertEqual(school.school_mascot, "Chaparrals")
		self.assertEqual(school.address, self.address)

	def test_school_name_max_length_is_100(self):
		field = HighSchool._meta.get_field("school_name")
		self.assertEqual(field.max_length, 100)

	def test_school_mascot_max_length_is_100(self):
		field = HighSchool._meta.get_field("school_mascot")
		self.assertEqual(field.max_length, 100)

	def test_school_mascot_allows_blank_and_null(self):
		field = HighSchool._meta.get_field("school_mascot")
		self.assertTrue(field.blank)
		self.assertTrue(field.null)

	def test_address_is_foreign_key_to_address_model(self):
		field = HighSchool._meta.get_field("address")
		self.assertEqual(field.related_model, Address)

	def test_address_allows_blank_and_null(self):
		field = HighSchool._meta.get_field("address")
		self.assertTrue(field.blank)
		self.assertTrue(field.null)

	def test_address_on_delete_is_do_nothing(self):
		field = HighSchool._meta.get_field("address")
		self.assertIs(field.remote_field.on_delete, models.DO_NOTHING)

	def test_address_related_name(self):
		field = HighSchool._meta.get_field("address")
		self.assertEqual(field.remote_field.related_name, "high_schools")

	def test_address_verbose_name(self):
		field = HighSchool._meta.get_field("address")
		self.assertEqual(field.verbose_name, "High School Address")

	def test_deleting_address_with_do_nothing_raises_integrity_error(self):
		school = HighSchool.objects.create(
			school_name="Westlake High School",
			school_mascot="Chaparrals",
			address=self.address,
		)

		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				Address.objects.filter(pk=self.address.pk).delete()

		self.assertTrue(HighSchool.objects.filter(pk=school.pk).exists())
