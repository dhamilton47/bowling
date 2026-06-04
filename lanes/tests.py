from django.test import TestCase
from address.models import Address, City, State

from lanes.models import Lanes


class LanesModelTests(TestCase):
	def setUp(self):
		self.state = State.objects.create(state="Texas", state_abbr="TX")
		self.city = City.objects.create(city="Austin", state=self.state, zip_code="78701")
		self.address = Address.objects.create(street1="100 Bowl Ave", city=self.city)

	def test_can_create_lanes_with_address(self):
		lanes = Lanes.objects.create(lanes="Highland Lanes", address=self.address)

		self.assertEqual(lanes.lanes, "Highland Lanes")
		self.assertEqual(lanes.address, self.address)

	def test_string_representation(self):
		lanes = Lanes.objects.create(lanes="Main Street Lanes", address=self.address)
		self.assertEqual(str(lanes), "Main Street Lanes")

	def test_meta_options(self):
		self.assertEqual(Lanes._meta.verbose_name, "Lanes")
		self.assertEqual(Lanes._meta.verbose_name_plural, "Lanes")
		self.assertEqual(Lanes._meta.ordering, ["lanes"])

	def test_address_delete_cascades_to_lanes(self):
		lanes = Lanes.objects.create(lanes="Strike Zone", address=self.address)
		self.address.delete()

		self.assertFalse(Lanes.objects.filter(pk=lanes.pk).exists())
