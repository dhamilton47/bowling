from django import forms

from game.models import Game
from openbowl.models import OpenBowlingActivity
from player.models import Player


class OpenBowlingCreateForm(forms.Form):
    players = forms.ModelMultipleChoiceField(
        queryset=Player.objects.select_related("person").all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
    )
    score_update_method = forms.ChoiceField(
        choices=Game.SCORE_UPDATE_CHOICES,
        initial=Game.SCORE_UPDATE_EACH_BALL,
    )


class OpenBowlingRollForm(forms.Form):
    frame_number = forms.IntegerField(min_value=1, max_value=10)
    ball_number = forms.IntegerField(min_value=1, max_value=3)
    pins = forms.IntegerField(min_value=0, max_value=10)
