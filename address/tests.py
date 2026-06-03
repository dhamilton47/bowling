from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from address.models import Address, City, State


class StateModelTests(TestCase):
	def test_state_string_representation(self):
		state = State.objects.create(state="California", state_abbr="CA")
		self.assertEqual(str(state), "CA - California")


class CityModelTests(TestCase):
	def setUp(self):
		self.state = State.objects.create(state="Texas", state_abbr="TX")

	def test_zip_code_accepts_five_digits(self):
		city = City(city="Austin", state=self.state, zip_code="78701")
		city.full_clean()

	def test_zip_code_accepts_zip_plus_four(self):
		city = City(city="Austin", state=self.state, zip_code="78701-1234")
		city.full_clean()

	def test_zip_code_rejects_invalid_format(self):
		city = City(city="Austin", state=self.state, zip_code="7870")
		with self.assertRaises(ValidationError):
			city.full_clean()

	def test_unique_together_city_state_zip(self):
		City.objects.create(city="Austin", state=self.state, zip_code="78701")
		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				City.objects.create(city="Austin", state=self.state, zip_code="78701")


class AddressModelTests(TestCase):
	def setUp(self):
		self.state = State.objects.create(state="Florida", state_abbr="FL")
		self.city = City.objects.create(city="Orlando", state=self.state, zip_code="32801")

	def test_address_string_with_street2(self):
		address = Address.objects.create(
			street1="123 Main St",
			street2="Apt 4B",
			city=self.city,
		)
		self.assertEqual(str(address), "123 Main St, Apt 4B, Orlando, FL 32801")

	def test_address_string_without_street2(self):
		address = Address.objects.create(
			street1="123 Main St",
			city=self.city,
		)
		self.assertEqual(str(address), "123 Main St, Orlando, FL 32801")

