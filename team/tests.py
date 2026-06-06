from django.test import TestCase
from django.db import models

from address.models import Address, City, State
from person.models import Person
from player.models import Player

from .models import Team


class TeamModelTests(TestCase):
	def setUp(self):
		self.state = State.objects.create(state="Texas", state_abbr="TX")
		self.city = City.objects.create(city="Austin", state=self.state, zip_code="78701")
		self.address = Address.objects.create(street1="100 Main St", city=self.city)

		self.person_one = Person.objects.create(
			address=self.address,
			first_name="John",
			last_name="Doe",
		)
		self.person_two = Person.objects.create(
			address=self.address,
			first_name="Jane",
			last_name="Smith",
		)

		self.player_one = Player.objects.create(person=self.person_one)
		self.player_two = Player.objects.create(person=self.person_two)

	def test_team_field_exists_with_max_length_100(self):
		field = Team._meta.get_field("team")
		self.assertIsInstance(field, models.CharField)
		self.assertEqual(field.max_length, 100)

	def test_team_field_allows_blank(self):
		field = Team._meta.get_field("team")
		self.assertTrue(field.blank)

	def test_team_field_allows_null(self):
		field = Team._meta.get_field("team")
		self.assertTrue(field.null)

	def test_players_field_is_many_to_many_to_player(self):
		field = Team._meta.get_field("players")
		self.assertIsInstance(field, models.ManyToManyField)
		self.assertEqual(field.related_model, Player)

	def test_players_field_allows_blank(self):
		field = Team._meta.get_field("players")
		self.assertTrue(field.blank)

	def test_can_create_team_and_add_players(self):
		team = Team.objects.create(team="The Strikers")
		team.players.add(self.player_one, self.player_two)

		self.assertEqual(team.team, "The Strikers")
		self.assertEqual(team.players.count(), 2)

	def test_team_string_representation_returns_team_name(self):
		team = Team.objects.create(team="The Rollers")
		self.assertEqual(str(team), "The Rollers")
