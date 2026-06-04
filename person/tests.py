from django.test import TestCase
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from address.models import Address, City, State
from .models import Person


class PersonModelTests(TestCase):
	def setUp(self):
		self.state = State.objects.create(state="Texas", state_abbr="TX")
		self.city = City.objects.create(city="Austin", state=self.state, zip_code="78701")
		self.address = Address.objects.create(street1="100 Main St", city=self.city)
		self.other_address = Address.objects.create(street1="200 Main St", city=self.city)

	def test_create_person_with_required_fields(self):
		person = Person.objects.create(
			address=self.address,
			first_name="John",
			last_name="Doe",
		)

		self.assertEqual(person.first_name, "John")
		self.assertEqual(person.last_name, "Doe")
		self.assertIsNone(person.middle_name)
		self.assertIsNone(person.preferred_name)
		self.assertEqual(person.suffix, "")

	def test_name_fields_allow_null(self):
		person = Person.objects.create(
			address=self.address,
			first_name=None,
			middle_name=None,
			last_name=None,
			preferred_name=None,
		)

		self.assertIsNone(person.first_name)
		self.assertIsNone(person.middle_name)
		self.assertIsNone(person.last_name)
		self.assertIsNone(person.preferred_name)

	def test_optional_name_fields_are_saved(self):
		person = Person.objects.create(
			address=self.address,
			first_name="James",
			middle_name="Tiberius",
			last_name="Kirk",
			preferred_name="Jim",
			suffix="Jr",
		)

		self.assertEqual(person.middle_name, "Tiberius")
		self.assertEqual(person.preferred_name, "Jim")
		self.assertEqual(person.suffix, "Jr")

	def test_created_and_updated_timestamps_are_set(self):
		person = Person.objects.create(address=self.address, first_name="Jane", last_name="Smith")

		self.assertIsNotNone(person.created_at)
		self.assertIsNotNone(person.updated_at)
		self.assertLessEqual(person.created_at, timezone.now())
		self.assertLessEqual(person.updated_at, timezone.now())

	def test_updated_at_changes_on_save(self):
		person = Person.objects.create(address=self.address, first_name="Janet", last_name="Lee")
		original_updated_at = person.updated_at

		person.preferred_name = "Jan"
		person.save()
		person.refresh_from_db()

		self.assertGreaterEqual(person.updated_at, original_updated_at)

	def test_db_constraint_rejects_empty_first_name(self):
		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				Person.objects.create(address=self.address, first_name="", last_name="Doe")

	def test_db_constraint_rejects_empty_last_name(self):
		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				Person.objects.create(address=self.address, first_name="John", last_name="")

	def test_duplicate_name_and_address_disallowed_without_suffix(self):
		Person.objects.create(address=self.address, first_name="John", last_name="Doe")
		with self.assertRaises(ValidationError):
			Person.objects.create(address=self.address, first_name="John", last_name="Doe")

	def test_duplicate_name_and_address_allowed_with_unique_non_empty_suffixes(self):
		Person.objects.create(address=self.address, first_name="John", last_name="Doe", suffix="Jr")
		person = Person.objects.create(address=self.address, first_name="John", last_name="Doe", suffix="Sr")
		self.assertEqual(person.suffix, "Sr")

	def test_duplicate_name_and_address_rejects_duplicate_suffix(self):
		Person.objects.create(address=self.address, first_name="John", last_name="Doe", suffix="III")
		with self.assertRaises(ValidationError):
			Person.objects.create(address=self.address, first_name="John", last_name="Doe", suffix="III")

	def test_duplicate_name_and_address_rejects_suffix_if_existing_record_has_empty_suffix(self):
		Person.objects.create(address=self.address, first_name="John", last_name="Doe")
		with self.assertRaises(ValidationError):
			Person.objects.create(address=self.address, first_name="John", last_name="Doe", suffix="Jr")

	def test_same_name_allowed_for_different_addresses(self):
		Person.objects.create(address=self.address, first_name="John", last_name="Doe")
		person = Person.objects.create(address=self.other_address, first_name="John", last_name="Doe")
		self.assertEqual(person.address_id, self.other_address.id)
