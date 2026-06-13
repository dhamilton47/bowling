from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from game.models import Game
from openbowl.forms import OpenBowlingCreateForm, OpenBowlingRollForm
from openbowl.models import OpenBowlingActivity, OpenBowlingActivityGame


def _next_open_bowling_sequence_number():
    last_sequence = OpenBowlingActivity.objects.order_by("-sequence_number").values_list("sequence_number", flat=True).first()
    if last_sequence is None:
        return 1
    return last_sequence + 1


@transaction.atomic
def _create_open_bowling_activity(players, score_update_method):
    activity = OpenBowlingActivity.objects.create(
        name="Open Bowling",
        sequence_number=_next_open_bowling_sequence_number(),
    )

    for idx, player in enumerate(players, start=1):
        game = Game.create_initialized_game(
            player=player,
            score_update_method=score_update_method,
            persist=True,
        )
        OpenBowlingActivityGame.objects.create(
            activity=activity,
            player=player,
            game=game,
            sort_order=idx,
        )

    return activity


def _apply_roll_to_game(game, frame_number, ball_number, pins):
    if frame_number < 1 or frame_number > 10:
        raise ValidationError("Frame number must be between 1 and 10.")
    if ball_number < 1 or ball_number > 3:
        raise ValidationError("Ball number must be between 1 and 3.")
    if frame_number < 10 and ball_number == 3:
        raise ValidationError("Only frame 10 can have ball 3.")

    frame = getattr(game, f"frame{frame_number}")
    ball = getattr(frame, f"ball{ball_number}", None)
    if ball is None:
        raise ValidationError("Selected ball does not exist for this frame.")

    frame.is_started = True
    if frame_number == 10 and ball_number == 3:
        frame.is_ball3 = True
    ball.pins = pins

    frame.clean()
    ball.save(update_fields=["pins", "updated_at"])
    frame.save(update_fields=["is_started", "is_ball3", "updated_at"])
    game.update_final_score(save=True)


def _build_scoresheet_frames(game):
    frames = []
    for frame_number in range(1, 11):
        frame = getattr(game, f"frame{frame_number}")
        marks = frame.get_ball_display_slots(placeholder="")
        frames.append(
            {
                "number": frame_number,
                "marks": marks,
                "running_total": frame.score_after if frame.score_after is not None else "",
            }
        )
    return frames


def _build_participant_sheets(entries, current_entry):
    sheets = []
    for entry in entries:
        sheets.append(
            {
                "entry": entry,
                "is_current": entry.id == current_entry.id,
                "frames": _build_scoresheet_frames(entry.game),
                "total": entry.game.final_score.score if entry.game.final_score is not None else 0,
                "admin_game_change_url": reverse("admin:game_game_change", args=[entry.game_id]),
            }
        )
    return sheets


def open_bowling_home(request):
    if request.method == "POST":
        form = OpenBowlingCreateForm(request.POST)
        if form.is_valid():
            players = list(form.cleaned_data["players"])
            score_update_method = form.cleaned_data["score_update_method"]
            activity = _create_open_bowling_activity(players, score_update_method)
            first_entry = activity.activity_games.order_by("sort_order", "id").first()
            if first_entry is None:
                messages.error(request, "Activity was created without players.")
                return redirect("openbowl:open_bowling_home")
            return redirect("openbowl:open_bowling_activity", activity_id=activity.id, player_pk=first_entry.player_id)
    else:
        form = OpenBowlingCreateForm()

    activities = OpenBowlingActivity.objects.prefetch_related(
        "activity_games__player__person",
        "activity_games__game__final_score",
    ).all()[:20]

    context = {
        "form": form,
        "activities": activities,
        "admin_url": reverse("admin:index"),
    }
    return render(request, "openbowl/open_bowling_home.html", context)


def open_bowling_activity(request, activity_id, player_pk=None):
    activity = get_object_or_404(
        OpenBowlingActivity.objects.prefetch_related(
            "activity_games__player__person",
            "activity_games__game__final_score",
        ),
        pk=activity_id,
    )

    entries = list(activity.activity_games.all())
    if not entries:
        messages.error(request, "This activity has no players.")
        return redirect("openbowl:open_bowling_home")

    current_entry = entries[0]
    if player_pk is not None:
        for entry in entries:
            if entry.player_id == player_pk:
                current_entry = entry
                break

    if request.method == "POST" and "repeat_activity" in request.POST:
        players = [entry.player for entry in entries]
        score_method = current_entry.game.score_update_method
        next_activity = _create_open_bowling_activity(players, score_method)
        next_first_entry = next_activity.activity_games.order_by("sort_order", "id").first()
        return redirect(
            "openbowl:open_bowling_activity",
            activity_id=next_activity.id,
            player_pk=next_first_entry.player_id,
        )

    roll_form = OpenBowlingRollForm(request.POST or None)
    if request.method == "POST" and "save_roll" in request.POST:
        if roll_form.is_valid():
            try:
                _apply_roll_to_game(
                    current_entry.game,
                    roll_form.cleaned_data["frame_number"],
                    roll_form.cleaned_data["ball_number"],
                    roll_form.cleaned_data["pins"],
                )
                messages.success(request, "Roll saved.")
                return redirect(
                    "openbowl:open_bowling_activity",
                    activity_id=activity.id,
                    player_pk=current_entry.player_id,
                )
            except ValidationError as exc:
                roll_form.add_error(None, exc)

    context = {
        "activity": activity,
        "entries": entries,
        "current_entry": current_entry,
        "current_game": current_entry.game,
        "participant_sheets": _build_participant_sheets(entries, current_entry),
        "roll_form": roll_form,
        "admin_url": reverse("admin:index"),
        "admin_game_changelist_url": reverse("admin:game_game_changelist"),
        "admin_game_change_url": reverse("admin:game_game_change", args=[current_entry.game_id]),
    }
    return render(request, "openbowl/open_bowling_activity.html", context)
