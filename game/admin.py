from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from game.models import Ball, FinalScore, Frame, Game


class HiddenFromAdminIndexMixin:
	def get_model_perms(self, request):
		return {}


@admin.register(Ball)
class BallAdmin(HiddenFromAdminIndexMixin, admin.ModelAdmin):
	list_display = ("id", "value", "pins", "created_at", "updated_at")
	search_fields = ("id",)


@admin.register(Frame)
class FrameAdmin(HiddenFromAdminIndexMixin, admin.ModelAdmin):
	list_display = ("id", "frame_number", "score_before", "score_after", "created_at", "updated_at")
	list_filter = ("is_started", "is_ball3", "is_bonus1", "is_bonus2")


@admin.register(FinalScore)
class FinalScoreAdmin(HiddenFromAdminIndexMixin, admin.ModelAdmin):
	list_display = ("id", "score", "is_final", "created_at", "updated_at")
	list_filter = ("is_final",)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
	list_display = ("id", "player", "is_final", "open_bowling_activity_link", "created_at", "updated_at")
	list_filter = ("is_final",)

	def has_add_permission(self, request):
		return False

	@admin.display(description="Open Bowling")
	def open_bowling_activity_link(self, obj):
		entry = getattr(obj, "open_bowling_entry", None)
		if entry is None:
			return "-"
		url = reverse("openbowl:open_bowling_activity", args=[entry.activity_id, entry.player_id])
		return format_html('<a href="{}">Open Activity</a>', url)
