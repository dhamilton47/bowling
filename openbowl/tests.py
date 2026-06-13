from django.test import TestCase
from django.urls import reverse

from address.models import Address, City, State
from openbowl.models import OpenBowlingActivity, OpenBowlingActivityGame
from person.models import Person
from player.models import Player


class OpenBowlingViewTests(TestCase):
    def setUp(self):
        self.state = State.objects.create(state="Texas", state_abbr="TX")
        self.city = City.objects.create(city="Austin", state=self.state, zip_code="78701")
        self.address = Address.objects.create(street1="100 Main St", city=self.city)

        self.player1 = self._create_player("Alex", "Archer")
        self.player2 = self._create_player("Blair", "Bowman")

    def _create_player(self, first_name, last_name):
        person = Person.objects.create(
            address=self.address,
            first_name=first_name,
            last_name=last_name,
        )
        return Player.objects.create(person=person)

    def test_open_bowling_home_post_creates_activity_and_games(self):
        response = self.client.post(
            reverse("openbowl:open_bowling_home"),
            {
                "players": [self.player1.pk, self.player2.pk],
                "score_update_method": "each_ball",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(OpenBowlingActivity.objects.count(), 1)
        self.assertEqual(OpenBowlingActivityGame.objects.count(), 2)

        activity = OpenBowlingActivity.objects.get()
        entries = list(activity.activity_games.select_related("game", "player").order_by("sort_order"))
        self.assertEqual(entries[0].player_id, self.player1.pk)
        self.assertEqual(entries[1].player_id, self.player2.pk)
        self.assertEqual(entries[0].game.score_update_method, "each_ball")

    def test_open_bowling_activity_save_roll_updates_game(self):
        self.client.post(
            reverse("openbowl:open_bowling_home"),
            {
                "players": [self.player1.pk],
                "score_update_method": "each_ball",
            },
        )
        entry = OpenBowlingActivityGame.objects.select_related("activity", "game").get()

        response = self.client.post(
            reverse("openbowl:open_bowling_activity", args=[entry.activity_id, entry.player_id]),
            {
                "frame_number": 1,
                "ball_number": 1,
                "pins": 8,
                "save_roll": "1",
            },
        )

        self.assertEqual(response.status_code, 302)
        entry.refresh_from_db()
        game = entry.game
        game.refresh_from_db()
        self.assertEqual(game.frame1.ball1.pins, 8)
        self.assertEqual(game.final_score.score, 8)

    def test_open_bowling_repeat_activity_clones_player_set(self):
        self.client.post(
            reverse("openbowl:open_bowling_home"),
            {
                "players": [self.player1.pk, self.player2.pk],
                "score_update_method": "defer_after_triple_strike",
            },
        )
        first_activity = OpenBowlingActivity.objects.get()
        first_entry = first_activity.activity_games.order_by("sort_order").first()

        response = self.client.post(
            reverse("openbowl:open_bowling_activity", args=[first_activity.id, first_entry.player_id]),
            {"repeat_activity": "1"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(OpenBowlingActivity.objects.count(), 2)

        second_activity = OpenBowlingActivity.objects.order_by("-sequence_number").first()
        second_entries = second_activity.activity_games.select_related("game", "player").order_by("sort_order")
        self.assertEqual(second_entries.count(), 2)
        self.assertEqual(second_entries[0].player_id, self.player1.pk)
        self.assertEqual(second_entries[1].player_id, self.player2.pk)
        self.assertEqual(second_entries[0].game.score_update_method, "defer_after_triple_strike")
