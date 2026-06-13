from django.test import TestCase
from django.db import models
from django.core.exceptions import ValidationError

from game.functions import BowlingGame
from game.models import Ball, FinalScore, Frame, Game
from player.models import Player


class TestBallModel(TestCase):
	model_name = "Ball"

	def assert_nullable_integer_with_default(self, field_name):
		field = Ball._meta.get_field(field_name)
		self.assertIsInstance(field, models.IntegerField)
		self.assertTrue(field.has_default())
		self.assertTrue(field.blank)
		self.assertTrue(field.null)

	def test_ball_has_expected_integer_fields(self):
		integer_fields = ["value", "pins"] + [f"pin{idx}" for idx in range(1, 11)]
		for field_name in integer_fields:
			with self.subTest(field=field_name):
				self.assert_nullable_integer_with_default(field_name)

	def test_ball_has_created_at(self):
		field = Ball._meta.get_field("created_at")
		self.assertIsInstance(field, models.DateTimeField)
		self.assertTrue(field.auto_now_add)

	def test_ball_has_updated_at(self):
		field = Ball._meta.get_field("updated_at")
		self.assertIsInstance(field, models.DateTimeField)
		self.assertTrue(field.auto_now)

	def test_determine_pins_sums_pin1_to_pin10(self):
		ball = Ball(
			pin1=1,
			pin2=0,
			pin3=1,
			pin4=0,
			pin5=1,
			pin6=0,
			pin7=1,
			pin8=0,
			pin9=1,
			pin10=0,
		)

		result = ball.determine_pins()

		self.assertEqual(result, 5)
		self.assertEqual(ball.pins, 5)


class TestFrameModel(TestCase):
	model_name = "Frame"

	def create_ball(self, pins):
		return Ball(pins=pins)

	def assert_nullable_integer(self, field_name):
		field = Frame._meta.get_field(field_name)
		self.assertIsInstance(field, models.IntegerField)
		self.assertTrue(field.blank)
		self.assertTrue(field.null)

	def assert_boolean_with_default(self, field_name):
		field = Frame._meta.get_field(field_name)
		self.assertIsInstance(field, models.BooleanField)
		self.assertTrue(field.has_default())

	def assert_nullable_ball_fk_with_related_name(self, field_name):
		field = Frame._meta.get_field(field_name)
		self.assertIsInstance(field, models.ForeignKey)
		self.assertIs(field.remote_field.on_delete, models.CASCADE)
		self.assertTrue(field.null)
		self.assertIs(field.remote_field.model, Ball)
		related_name = field.remote_field.related_name
		self.assertIsNotNone(related_name)
		self.assertNotEqual(related_name, "")

	def test_frame_has_expected_integer_fields(self):
		for field_name in ["frame_number", "score_before", "bonus1", "bonus2", "score_after"]:
			with self.subTest(field=field_name):
				self.assert_nullable_integer(field_name)

	def test_frame_has_expected_boolean_fields(self):
		for field_name in ["is_started", "is_ball3", "is_bonus1", "is_bonus2"]:
			with self.subTest(field=field_name):
				self.assert_boolean_with_default(field_name)

	def test_frame_has_expected_ball_foreign_keys(self):
		for field_name in ["ball1", "ball2", "ball3"]:
			with self.subTest(field=field_name):
				self.assert_nullable_ball_fk_with_related_name(field_name)

	def test_frame_has_created_at(self):
		field = Frame._meta.get_field("created_at")
		self.assertIsInstance(field, models.DateTimeField)
		self.assertTrue(field.auto_now_add)

	def test_frame_has_updated_at(self):
		field = Frame._meta.get_field("updated_at")
		self.assertIsInstance(field, models.DateTimeField)
		self.assertTrue(field.auto_now)

	def test_clean_accepts_valid_open_frame(self):
		frame = Frame(
			frame_number=1,
			ball1=self.create_ball(3),
			ball2=self.create_ball(6),
		)

		frame.clean()

	def test_clean_rejects_open_frame_over_ten(self):
		frame = Frame(
			frame_number=1,
			ball1=self.create_ball(7),
			ball2=self.create_ball(5),
		)

		with self.assertRaises(ValidationError):
			frame.clean()

	def test_clean_rejects_third_ball_before_tenth(self):
		frame = Frame(
			frame_number=9,
			ball1=self.create_ball(10),
			ball3=self.create_ball(10),
		)

		with self.assertRaises(ValidationError):
			frame.clean()

	def test_clean_accepts_tenth_frame_third_ball_after_mark(self):
		frame = Frame(
			frame_number=10,
			ball1=self.create_ball(10),
			ball2=self.create_ball(7),
			ball3=self.create_ball(2),
		)

		frame.clean()

	def test_clean_rejects_tenth_frame_third_ball_without_mark(self):
		frame = Frame(
			frame_number=10,
			ball1=self.create_ball(4),
			ball2=self.create_ball(4),
			ball3=self.create_ball(1),
		)

		with self.assertRaises(ValidationError):
			frame.clean()

	def test_get_ball_display_values_for_open_frame(self):
		frame = Frame(
			frame_number=1,
			ball1=self.create_ball(3),
			ball2=self.create_ball(6),
		)

		self.assertEqual(frame.get_ball_display_values(), ["3", "6"])

	def test_get_ball_display_values_for_spare_frame(self):
		frame = Frame(
			frame_number=1,
			ball1=self.create_ball(7),
			ball2=self.create_ball(3),
		)

		self.assertEqual(frame.get_ball_display_values(), ["7", "/"])

	def test_get_ball_display_values_for_strike_frame(self):
		frame = Frame(
			frame_number=1,
			ball1=self.create_ball(10),
		)

		self.assertEqual(frame.get_ball_display_values(), ["X"])

	def test_get_ball_display_values_for_miss(self):
		frame = Frame(
			frame_number=1,
			ball1=self.create_ball(0),
			ball2=self.create_ball(9),
		)

		self.assertEqual(frame.get_ball_display_values(), ["-", "9"])

	def test_get_ball_display_values_for_tenth_strike_then_spare(self):
		frame = Frame(
			frame_number=10,
			ball1=self.create_ball(10),
			ball2=self.create_ball(7),
			ball3=self.create_ball(3),
		)

		self.assertEqual(frame.get_ball_display_values(), ["X", "7", "/"])

	def test_get_ball_display_values_for_tenth_spare_then_fill_ball(self):
		frame = Frame(
			frame_number=10,
			ball1=self.create_ball(8),
			ball2=self.create_ball(2),
			ball3=self.create_ball(10),
		)

		self.assertEqual(frame.get_ball_display_values(), ["8", "/", "X"])

	def test_get_ball_display_slots_pads_regular_frame(self):
		frame = Frame(
			frame_number=1,
			ball1=self.create_ball(10),
		)

		self.assertEqual(frame.get_ball_display_slots(), ["X", ""])

	def test_get_ball_display_slots_pads_tenth_frame(self):
		frame = Frame(
			frame_number=10,
			ball1=self.create_ball(8),
			ball2=self.create_ball(2),
		)

		self.assertEqual(frame.get_ball_display_slots(), ["8", "/", ""])

	def test_get_ball_display_slots_supports_custom_placeholder(self):
		frame = Frame(
			frame_number=1,
			ball1=self.create_ball(4),
		)

		self.assertEqual(frame.get_ball_display_slots("_"), ["4", "_"])


class TestFinalScoreModel(TestCase):
	model_name = "FinalScore"

	def test_final_score_has_score_integer_field(self):
		field = FinalScore._meta.get_field("score")
		self.assertIsInstance(field, models.IntegerField)
		self.assertTrue(field.blank)
		self.assertTrue(field.null)

	def test_final_score_has_is_final_boolean_field(self):
		field = FinalScore._meta.get_field("is_final")
		self.assertIsInstance(field, models.BooleanField)
		self.assertTrue(field.has_default())
		self.assertFalse(field.default)

	def test_final_score_has_created_at(self):
		field = FinalScore._meta.get_field("created_at")
		self.assertIsInstance(field, models.DateTimeField)
		self.assertTrue(field.auto_now_add)

	def test_final_score_has_updated_at(self):
		field = FinalScore._meta.get_field("updated_at")
		self.assertIsInstance(field, models.DateTimeField)
		self.assertTrue(field.auto_now)


class TestGameModel(TestCase):
	model_name = "Game"

	def create_ball(self, pins):
		return Ball.objects.create(pins=pins)

	def assert_frame_foreign_key(self, field_name):
		field = Game._meta.get_field(field_name)
		self.assertIsInstance(field, models.ForeignKey)
		self.assertIs(field.remote_field.model, Frame)
		self.assertIs(field.remote_field.on_delete, models.CASCADE)
		self.assertTrue(field.blank)
		self.assertTrue(field.null)
		related_name = field.remote_field.related_name
		self.assertIsNotNone(related_name)
		self.assertNotEqual(related_name, "")

	def test_game_has_player_foreign_key(self):
		field = Game._meta.get_field("player")
		self.assertIsInstance(field, models.ForeignKey)
		self.assertIs(field.remote_field.model, Player)
		self.assertIs(field.remote_field.on_delete, models.DO_NOTHING)
		self.assertTrue(field.null)

	def test_game_has_frame1_to_frame10_foreign_keys(self):
		for idx in range(1, 11):
			field_name = f"frame{idx}"
			with self.subTest(field=field_name):
				self.assert_frame_foreign_key(field_name)

	def test_game_has_final_score_one_to_one_field(self):
		field = Game._meta.get_field("final_score")
		self.assertIsInstance(field, models.OneToOneField)
		self.assertIs(field.remote_field.model, FinalScore)
		self.assertIs(field.remote_field.on_delete, models.CASCADE)
		self.assertTrue(field.null)

	def test_game_has_is_final_boolean_field(self):
		field = Game._meta.get_field("is_final")
		self.assertIsInstance(field, models.BooleanField)
		self.assertTrue(field.has_default())
		self.assertFalse(field.default)

	def test_game_has_score_update_method_field(self):
		field = Game._meta.get_field("score_update_method")
		self.assertIsInstance(field, models.CharField)
		self.assertTrue(field.has_default())
		self.assertEqual(field.default, Game.SCORE_UPDATE_EACH_BALL)

	def test_game_has_created_at(self):
		field = Game._meta.get_field("created_at")
		self.assertIsInstance(field, models.DateTimeField)
		self.assertTrue(field.auto_now_add)

	def test_game_has_updated_at(self):
		field = Game._meta.get_field("updated_at")
		self.assertIsInstance(field, models.DateTimeField)
		self.assertTrue(field.auto_now)

	def test_game_init_builds_default_subparts(self):
		game = Game()

		for frame_number in range(1, 11):
			frame = getattr(game, f"frame{frame_number}")
			self.assertIsNotNone(frame)
			self.assertEqual(frame.frame_number, frame_number)
			self.assertIsNotNone(frame.ball1)
			self.assertIsNotNone(frame.ball2)
			if frame_number == 10:
				self.assertIsNotNone(frame.ball3)
			else:
				self.assertIsNone(frame.ball3)

		self.assertIsNotNone(game.final_score)
		self.assertEqual(game.final_score.score, 0)

	def test_create_initialized_game_builds_expected_unsaved_objects(self):
		game = Game.create_initialized_game()

		self.assertIsNone(game.pk)
		for frame_number in range(1, 11):
			frame = getattr(game, f"frame{frame_number}")
			self.assertIsNotNone(frame)
			self.assertEqual(frame.frame_number, frame_number)
			self.assertIsNone(frame.pk)
			self.assertIsNone(frame.ball1.pk)
			self.assertIsNone(frame.ball2.pk)
			if frame_number == 10:
				self.assertIsNotNone(frame.ball3)
				self.assertIsNone(frame.ball3.pk)
			else:
				self.assertIsNone(frame.ball3)

		self.assertIsNotNone(game.final_score)
		self.assertIsNone(game.final_score.pk)
		self.assertEqual(game.final_score.score, 0)

	def test_create_initialized_game_can_persist_all_components(self):
		game = Game.create_initialized_game(persist=True)

		self.assertIsNotNone(game.pk)
		for frame_number in range(1, 11):
			frame = getattr(game, f"frame{frame_number}")
			self.assertIsNotNone(frame.pk)
			self.assertIsNotNone(frame.ball1.pk)
			self.assertIsNotNone(frame.ball2.pk)
			if frame_number == 10:
				self.assertIsNotNone(frame.ball3.pk)
			else:
				self.assertIsNone(frame.ball3)

		self.assertIsNotNone(game.final_score.pk)
		self.assertEqual(game.final_score.score, 0)

	def test_game_init_respects_explicit_components(self):
		frame1 = Frame(frame_number=1, ball1=Ball(pins=2), ball2=Ball(pins=3))
		final_score = FinalScore(score=123)

		game = Game(frame1=frame1, final_score=final_score)

		self.assertIs(game.frame1, frame1)
		self.assertIs(game.final_score, final_score)

	def test_can_instantiate_full_game_with_all_subparts(self):
		frame1 = Frame.objects.create(
			frame_number=1,
			ball1=self.create_ball(8),
			ball2=self.create_ball(1),
			is_started=True,
			is_bonus1=True,
			is_bonus2=True,
		)
		frame2 = Frame.objects.create(
			frame_number=2,
			ball1=self.create_ball(7),
			ball2=self.create_ball(3),
			is_started=True,
			is_bonus1=True,
		)
		frame3 = Frame.objects.create(frame_number=3, ball1=self.create_ball(4), ball2=self.create_ball(5), is_started=True)
		frame4 = Frame.objects.create(frame_number=4, ball1=self.create_ball(6), ball2=self.create_ball(2), is_started=True)
		frame5 = Frame.objects.create(frame_number=5, ball1=self.create_ball(3), ball2=self.create_ball(6), is_started=True)
		frame6 = Frame.objects.create(frame_number=6, ball1=self.create_ball(8), ball2=self.create_ball(1), is_started=True)
		frame7 = Frame.objects.create(frame_number=7, ball1=self.create_ball(2), ball2=self.create_ball(7), is_started=True)
		frame8 = Frame.objects.create(frame_number=8, ball1=self.create_ball(5), ball2=self.create_ball(4), is_started=True)
		frame9 = Frame.objects.create(frame_number=9, ball1=self.create_ball(9), ball2=self.create_ball(0), is_started=True)
		frame10 = Frame.objects.create(
			frame_number=10,
			ball1=self.create_ball(10),
			ball2=self.create_ball(7),
			ball3=self.create_ball(2),
			is_started=True,
			is_ball3=True,
		)

		for frame in [frame1, frame2, frame3, frame4, frame5, frame6, frame7, frame8, frame9, frame10]:
			frame.clean()

		final_score = FinalScore.objects.create(score=156, is_final=True)

		game = Game.objects.create(
			frame1=frame1,
			frame2=frame2,
			frame3=frame3,
			frame4=frame4,
			frame5=frame5,
			frame6=frame6,
			frame7=frame7,
			frame8=frame8,
			frame9=frame9,
			frame10=frame10,
			final_score=final_score,
			is_final=True,
		)

		self.assertEqual(game.final_score.score, 156)
		self.assertTrue(game.is_final)

		expected_ball_counts = {
			1: 2,
			2: 2,
			3: 2,
			4: 2,
			5: 2,
			6: 2,
			7: 2,
			8: 2,
			9: 2,
			10: 3,
		}
		for frame_number in range(1, 11):
			frame = getattr(game, f"frame{frame_number}")
			self.assertIsNotNone(frame)
			ball_count = sum(1 for ball in [frame.ball1, frame.ball2, frame.ball3] if ball is not None)
			self.assertEqual(ball_count, expected_ball_counts[frame_number])

		self.assertTrue(game.frame1.is_bonus1)
		self.assertTrue(game.frame1.is_bonus2)
		self.assertTrue(game.frame10.is_ball3)

	def test_update_final_score_each_ball_mode(self):
		game = Game.create_initialized_game(
			score_update_method=Game.SCORE_UPDATE_EACH_BALL,
		)

		game.frame1.is_started = True
		game.frame1.ball1.pins = 10
		game.frame2.is_started = True
		game.frame2.ball1.pins = 7
		game.frame2.ball2.pins = 2

		score = game.update_final_score()

		self.assertEqual(score, 19)
		self.assertEqual(game.final_score.score, 19)

	def test_update_final_score_deferred_triple_strike_mode(self):
		game = Game.create_initialized_game(
			score_update_method=Game.SCORE_UPDATE_DEFER_AFTER_TRIPLE_STRIKE,
		)

		game.frame1.is_started = True
		game.frame1.ball1.pins = 10
		game.frame2.is_started = True
		game.frame2.ball1.pins = 10
		game.frame3.is_started = True
		game.frame3.ball1.pins = 10
		game.frame4.is_started = True
		game.frame4.ball1.pins = 10
		game.frame5.is_started = True
		game.frame5.ball1.pins = 6
		game.frame5.ball2.pins = 1

		score = game.update_final_score()

		self.assertEqual(score, 47)
		self.assertEqual(game.final_score.score, 47)


class TestGameBowlingGameIntegration(TestCase):
	def _apply_roll_to_game(self, game, frame_number, ball_index, pins):
		"""Apply one roll to a Game and return next frame/ball cursor."""
		frame = getattr(game, f"frame{frame_number}")
		frame.is_started = True

		if frame_number < 10:
			if ball_index == 1:
				frame.ball1.pins = pins
				if pins == 10:
					return frame_number + 1, 1
				return frame_number, 2

			frame.ball2.pins = pins
			return frame_number + 1, 1

		if ball_index == 1:
			frame.ball1.pins = pins
			return frame_number, 2

		if ball_index == 2:
			frame.ball2.pins = pins
			return frame_number, 3

		frame.ball3.pins = pins
		return frame_number, 4

	def _count_completed_game_frames(self, game):
		completed = 0
		for frame_number in range(1, 10):
			frame = getattr(game, f"frame{frame_number}")
			if not frame.is_started or frame.ball1 is None or frame.ball1.pins is None:
				continue
			if frame.ball1.pins == 10 or (frame.ball2 is not None and frame.ball2.pins is not None):
				completed += 1
		return completed

	def test_each_ball_mode_matches_running_pinfall_with_shared_roll_stream(self):
		rolls = [10, 7, 2, 4, 5, 10, 0, 8]
		bowling_game = BowlingGame()
		game = Game.create_initialized_game(score_update_method=Game.SCORE_UPDATE_EACH_BALL)

		frame_number = 1
		ball_index = 1
		running_total = 0

		for pins in rolls:
			bowling_game.roll(pins)
			frame_number, ball_index = self._apply_roll_to_game(game, frame_number, ball_index, pins)
			running_total += pins

			self.assertEqual(game.update_final_score(), running_total)
			self.assertEqual(self._count_completed_game_frames(game), len(bowling_game.frames))

	def test_deferred_mode_matches_current_running_scores_with_shared_roll_stream(self):
		rolls = [10, 10, 10, 10, 10, 6, 1]
		expected_running_scores = [10, 20, 30, 40, 50, 56, 57]
		bowling_game = BowlingGame()
		game = Game.create_initialized_game(
			score_update_method=Game.SCORE_UPDATE_DEFER_AFTER_TRIPLE_STRIKE,
		)

		frame_number = 1
		ball_index = 1

		for pins, expected_score in zip(rolls, expected_running_scores):
			bowling_game.roll(pins)
			frame_number, ball_index = self._apply_roll_to_game(game, frame_number, ball_index, pins)

			self.assertEqual(game.update_final_score(), expected_score)
			self.assertEqual(self._count_completed_game_frames(game), len(bowling_game.frames))
