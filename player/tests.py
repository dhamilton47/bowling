from django.test import TestCase
from django.db import IntegrityError, models, transaction

from address.models import Address, City, State
from person.models import Person
from student.models import Student

from player.models import Player


class PlayerModelTests(TestCase):
	def setUp(self):
		self.state = State.objects.create(state="Texas", state_abbr="TX")
		self.city = City.objects.create(city="Austin", state=self.state, zip_code="78701")
		self.address = Address.objects.create(street1="100 Main St", city=self.city)
		self.person = Person.objects.create(
			address=self.address,
			first_name="John",
			last_name="Doe",
		)

	def test_has_one_to_one_relation_to_person(self):
		field = Player._meta.get_field("person")
		self.assertIsInstance(field, models.OneToOneField)
		self.assertEqual(field.related_model, Person)

	def test_can_create_player_for_person(self):
		player = Player.objects.create(person=self.person)
		self.assertEqual(player.person, self.person)

	def test_person_relation_is_unique(self):
		Player.objects.create(person=self.person)

		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				Player.objects.create(person=self.person)

	def test_created_and_updated_timestamp_fields_exist(self):
		created_field = Player._meta.get_field("created_at")
		updated_field = Player._meta.get_field("updated_at")

		self.assertIsInstance(created_field, models.DateTimeField)
		self.assertIsInstance(updated_field, models.DateTimeField)
		self.assertTrue(created_field.auto_now_add)
		self.assertTrue(updated_field.auto_now)

	def test_string_representation_returns_string(self):
		player = Player.objects.create(person=self.person)
		self.assertIsInstance(str(player), str)

	def test_bowler_boolean_fields_exist(self):
		high_school_field = Player._meta.get_field("is_high_school_bowler")
		league_field = Player._meta.get_field("is_league_bowler")
		tournament_field = Player._meta.get_field("is_tournament_bowler")

		self.assertIsInstance(high_school_field, models.BooleanField)
		self.assertIsInstance(league_field, models.BooleanField)
		self.assertIsInstance(tournament_field, models.BooleanField)

	def test_bowler_boolean_fields_default_to_false(self):
		player = Player.objects.create(person=self.person)

		self.assertFalse(player.is_high_school_bowler)
		self.assertFalse(player.is_league_bowler)
		self.assertFalse(player.is_tournament_bowler)

	def test_bowler_boolean_fields_can_be_set_true(self):
		player = Player.objects.create(
			person=self.person,
			is_high_school_bowler=True,
			is_league_bowler=True,
			is_tournament_bowler=True,
		)

		self.assertTrue(player.is_high_school_bowler)
		self.assertTrue(player.is_league_bowler)
		self.assertTrue(player.is_tournament_bowler)

	def test_student_field_links_to_student_model(self):
		field = Player._meta.get_field("student")
		self.assertEqual(field.related_model, Student)

	def test_student_field_allows_blank_and_null(self):
		field = Player._meta.get_field("student")
		self.assertTrue(field.blank)
		self.assertTrue(field.null)

	def test_student_field_verbose_name(self):
		field = Player._meta.get_field("student")
		self.assertEqual(field.verbose_name, "Student")
