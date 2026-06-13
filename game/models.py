from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction

from player.models import Player


class Ball(models.Model):
	value = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pins = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin1 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin2 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin3 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin4 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin5 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin6 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin7 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin8 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin9 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	pin10 = models.IntegerField(
		default=0,
		blank=True,
		null=True
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def determine_pins(self):
		pin_total = sum(
			(getattr(self, f"pin{idx}") or 0)
			for idx in range(1, 11)
		)
		self.pins = pin_total
		return pin_total


class Frame(models.Model):
	frame_number = models.IntegerField(
		blank=True,
		null=True
	)
	score_before = models.IntegerField(
		blank=True,
		null=True
	)
	bonus1 = models.IntegerField(
		blank=True,
		null=True
	)
	bonus2 = models.IntegerField(
		blank=True,
		null=True
	)
	score_after = models.IntegerField(
		blank=True,
		null=True
	)
	is_started = models.BooleanField(default=False)
	is_ball3 = models.BooleanField(default=False)
	is_bonus1 = models.BooleanField(default=False)
	is_bonus2 = models.BooleanField(default=False)
	ball1 = models.ForeignKey(
		Ball,
		on_delete=models.CASCADE,
		null=True,
		related_name="frame_ball1",
	)
	ball2 = models.ForeignKey(
		Ball,
		on_delete=models.CASCADE,
		null=True,
		related_name="frame_ball2",
	)
	ball3 = models.ForeignKey(
		Ball,
		on_delete=models.CASCADE,
		null=True,
		related_name="frame_ball3",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def _pins_for_ball(self, ball):
		if ball is None:
			return None
		return ball.pins or 0

	def _pins_to_symbol(self, pins):
		if pins == 0:
			return "-"
		return str(pins)

	def get_ball_display_values(self):
		"""Return score-sheet symbols for each thrown ball in this frame."""
		ball1_pins = self._pins_for_ball(self.ball1)
		ball2_pins = self._pins_for_ball(self.ball2)
		ball3_pins = self._pins_for_ball(self.ball3)

		symbols = []
		if ball1_pins is None:
			return symbols

		symbols.append("X" if ball1_pins == 10 else self._pins_to_symbol(ball1_pins))

		if ball2_pins is None:
			return symbols

		is_tenth = self.frame_number == 10
		if ball1_pins < 10 and ball1_pins + ball2_pins == 10:
			symbols.append("/")
		else:
			symbols.append("X" if ball2_pins == 10 else self._pins_to_symbol(ball2_pins))

		if ball3_pins is None:
			return symbols

		if is_tenth and ball1_pins == 10 and ball2_pins < 10 and ball2_pins + ball3_pins == 10:
			symbols.append("/")
		else:
			symbols.append("X" if ball3_pins == 10 else self._pins_to_symbol(ball3_pins))

		return symbols

	def get_ball_display_slots(self, placeholder=""):
		"""Return fixed display slots padded for unthrown balls.

		Frames 1-9 render two slots and frame 10 renders three slots.
		"""
		expected_slots = 3 if self.frame_number == 10 else 2
		symbols = self.get_ball_display_values()
		missing_slots = max(0, expected_slots - len(symbols))
		return symbols + [placeholder] * missing_slots

	def clean(self):
		super().clean()

		errors = []
		frame_number = self.frame_number
		if frame_number is None:
			errors.append("Frame number is required for scoring validation.")
		elif frame_number < 1 or frame_number > 10:
			errors.append("Frame number must be between 1 and 10.")

		ball1_pins = self._pins_for_ball(self.ball1)
		ball2_pins = self._pins_for_ball(self.ball2)
		ball3_pins = self._pins_for_ball(self.ball3)

		for label, pins in (("ball1", ball1_pins), ("ball2", ball2_pins), ("ball3", ball3_pins)):
			if pins is not None and (pins < 0 or pins > 10):
				errors.append(f"{label} pins must be between 0 and 10.")

		if errors:
			raise ValidationError(errors)

		if frame_number is None or ball1_pins is None:
			return

		is_tenth = frame_number == 10

		if not is_tenth:
			if ball1_pins == 10:
				if ball2_pins is not None:
					errors.append("Frames 1-9 cannot have ball2 after a strike.")
				if ball3_pins is not None:
					errors.append("Frames 1-9 cannot have ball3.")
			else:
				if ball2_pins is not None and ball1_pins + ball2_pins > 10:
					errors.append("Frames 1-9 cannot exceed 10 pins across ball1 and ball2.")
				if ball3_pins is not None:
					errors.append("Frames 1-9 cannot have ball3.")
		else:
			if ball2_pins is not None and ball1_pins != 10 and ball1_pins + ball2_pins > 10:
				errors.append("In frame 10, non-strike ball1 and ball2 cannot exceed 10 pins.")

			if ball3_pins is not None:
				made_mark_in_first_two = (
					ball1_pins == 10
					or (ball2_pins is not None and ball1_pins + ball2_pins == 10)
				)
				if not made_mark_in_first_two:
					errors.append("In frame 10, ball3 is only allowed after a strike or spare.")
				if ball1_pins == 10 and ball2_pins is not None and ball2_pins < 10 and ball2_pins + ball3_pins > 10:
					errors.append("In frame 10 after strike, non-strike ball2 and ball3 cannot exceed 10 pins.")

		if errors:
			raise ValidationError(errors)


class FinalScore(models.Model):
	score = models.IntegerField(
		blank=True,
		null=True,
	)
	is_final = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class Game(models.Model):
	SCORE_UPDATE_EACH_BALL = "each_ball"
	SCORE_UPDATE_DEFER_AFTER_TRIPLE_STRIKE = "defer_after_triple_strike"
	SCORE_UPDATE_CHOICES = [
		(SCORE_UPDATE_EACH_BALL, "Update after each ball"),
		(
			SCORE_UPDATE_DEFER_AFTER_TRIPLE_STRIKE,
			"Update after each ball until three strikes, then at end of strike streak",
		),
	]

	player = models.ForeignKey(
		Player,
		on_delete=models.DO_NOTHING,
		blank=True,
		null=True,
	)
	frame1 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame1",
	)
	frame2 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame2",
	)
	frame3 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame3",
	)
	frame4 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame4",
	)
	frame5 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame5",
	)
	frame6 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame6",
	)
	frame7 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame7",
	)
	frame8 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame8",
	)
	frame9 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame9",
	)
	frame10 = models.ForeignKey(
		Frame,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name="game_frame10",
	)
	final_score = models.OneToOneField(
		FinalScore,
		on_delete=models.CASCADE,
		null=True,
	)
	score_update_method = models.CharField(
		max_length=32,
		choices=SCORE_UPDATE_CHOICES,
		default=SCORE_UPDATE_EACH_BALL,
	)
	is_final = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	@staticmethod
	def _build_default_frame(frame_number):
		ball1 = Ball(value=None, pins=None)
		ball2 = Ball(value=None, pins=None)
		ball3 = Ball(value=None, pins=None) if frame_number == 10 else None
		return Frame(
			frame_number=frame_number,
			ball1=ball1,
			ball2=ball2,
			ball3=ball3,
		)

	@classmethod
	def create_initialized_game(cls, player=None, score_update_method=None, persist=False):
		"""Create a game with 10 frames and a final score container.

		If persist is False, returned objects are unsaved model instances.
		If persist is True, game and all subparts are saved and linked.
		"""
		method = score_update_method or cls.SCORE_UPDATE_EACH_BALL

		if not persist:
			game = cls(player=player, score_update_method=method)
			for frame_number in range(1, 11):
				setattr(game, f"frame{frame_number}", cls._build_default_frame(frame_number))
			game.final_score = FinalScore(score=0, is_final=False)
			return game

		with transaction.atomic():
			final_score = FinalScore.objects.create(score=0, is_final=False)
			frame_kwargs = {}
			for frame_number in range(1, 11):
				ball1 = Ball.objects.create(value=None, pins=None)
				ball2 = Ball.objects.create(value=None, pins=None)
				ball3 = Ball.objects.create(value=None, pins=None) if frame_number == 10 else None

				frame = Frame.objects.create(
					frame_number=frame_number,
					ball1=ball1,
					ball2=ball2,
					ball3=ball3,
				)
				frame_kwargs[f"frame{frame_number}"] = frame

			return cls.objects.create(
				player=player,
				final_score=final_score,
				score_update_method=method,
				**frame_kwargs,
			)

	def _iter_frames(self):
		for frame_number in range(1, 11):
			frame = getattr(self, f"frame{frame_number}", None)
			if frame is not None:
				yield frame

	def _collect_thrown_ball_pins(self):
		"""Collect thrown-ball pinfall in game order, skipping unthrown balls."""
		pins = []
		for frame in self._iter_frames():
			if not frame.is_started:
				continue

			ball1_pins = frame.ball1.pins if frame.ball1 is not None else None
			ball2_pins = frame.ball2.pins if frame.ball2 is not None else None
			ball3_pins = frame.ball3.pins if frame.ball3 is not None else None

			if ball1_pins is not None:
				pins.append(ball1_pins)

			if frame.frame_number != 10 and ball1_pins == 10:
				continue

			if ball2_pins is not None:
				pins.append(ball2_pins)

			if frame.frame_number == 10 and ball3_pins is not None:
				pins.append(ball3_pins)

		return pins

	def _calculate_final_score_each_ball(self):
		return sum(self._collect_thrown_ball_pins())

	def _calculate_final_score_deferred_triple_strike(self):
		"""Defer score updates during strike streaks after three consecutive strikes."""
		score = 0
		buffered = 0
		consecutive_strikes = 0
		is_deferring = False

		for pinfall in self._collect_thrown_ball_pins():
			if pinfall == 10:
				consecutive_strikes += 1
			else:
				consecutive_strikes = 0

			if is_deferring:
				if pinfall == 10:
					buffered += pinfall
					continue
				score += buffered + pinfall
				buffered = 0
				is_deferring = False
				continue

			if pinfall == 10 and consecutive_strikes > 3:
				is_deferring = True
				buffered += pinfall
				continue

			score += pinfall

		if buffered:
			score += buffered

		return score

	def update_final_score(self, save=False):
		if self.final_score is None:
			self.final_score = FinalScore(score=0, is_final=False)

		if self.score_update_method == self.SCORE_UPDATE_DEFER_AFTER_TRIPLE_STRIKE:
			new_score = self._calculate_final_score_deferred_triple_strike()
		else:
			new_score = self._calculate_final_score_each_ball()

		self.final_score.score = new_score

		if save:
			if self.final_score.pk is None:
				self.final_score.save()
			self.save(update_fields=["final_score", "updated_at"])
			self.final_score.save(update_fields=["score", "updated_at"])

		return new_score

	def __init__(self, *args, **kwargs):
		frame_keys = [f"frame{idx}" for idx in range(1, 11)]
		explicit_component_input = any(key in kwargs for key in frame_keys + ["final_score"])
		super().__init__(*args, **kwargs)

		if explicit_component_input:
			return

		frame_id_fields = [f"frame{idx}_id" for idx in range(1, 11)]
		has_existing_component_ids = any(getattr(self, field_name, None) is not None for field_name in frame_id_fields)
		has_existing_component_ids = has_existing_component_ids or getattr(self, "final_score_id", None) is not None
		if has_existing_component_ids:
			return

		for frame_number in range(1, 11):
			frame = self._build_default_frame(frame_number)
			setattr(self, f"frame{frame_number}", frame)

		self.final_score = FinalScore(score=0, is_final=False)
	
	def __str__(self):
		return f"Game for Player {self.player}"
