from django import forms

from game.models import Ball, Frame, Game


class BallForm(forms.ModelForm):
	class Meta:
		model = Ball
		fields = [
			"value",
			"pins",
			"pin1",
			"pin2",
			"pin3",
			"pin4",
			"pin5",
			"pin6",
			"pin7",
			"pin8",
			"pin9",
			"pin10",
		]
		widgets = {
			"value": forms.NumberInput(attrs={"min": 0, "max": 10}),
			"pins": forms.NumberInput(attrs={"min": 0, "max": 10}),
			"pin1": forms.NumberInput(attrs={"min": 0, "max": 1}),
			"pin2": forms.NumberInput(attrs={"min": 0, "max": 1}),
			"pin3": forms.NumberInput(attrs={"min": 0, "max": 1}),
			"pin4": forms.NumberInput(attrs={"min": 0, "max": 1}),
			"pin5": forms.NumberInput(attrs={"min": 0, "max": 1}),
			"pin6": forms.NumberInput(attrs={"min": 0, "max": 1}),
			"pin7": forms.NumberInput(attrs={"min": 0, "max": 1}),
			"pin8": forms.NumberInput(attrs={"min": 0, "max": 1}),
			"pin9": forms.NumberInput(attrs={"min": 0, "max": 1}),
			"pin10": forms.NumberInput(attrs={"min": 0, "max": 1}),
		}


class FrameForm(forms.ModelForm):
	class Meta:
		model = Frame
		fields = [
			"frame_number",
			"score_before",
			"bonus1",
			"bonus2",
			"score_after",
			"is_started",
			"is_ball3",
			"is_bonus1",
			"is_bonus2",
			"ball1",
			"ball2",
			"ball3",
		]
		widgets = {
			"frame_number": forms.NumberInput(attrs={"min": 1, "max": 10}),
		}


class GameForm(forms.ModelForm):
	class Meta:
		model = Game
		fields = [
			"player",
			"frame1",
			"frame2",
			"frame3",
			"frame4",
			"frame5",
			"frame6",
			"frame7",
			"frame8",
			"frame9",
			"frame10",
			"final_score",
			"score_update_method",
			"is_final",
		]
