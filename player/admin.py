from django.contrib import admin
from player.models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
	list_display = ("person", "student", "is_high_school_bowler", "is_league_bowler", "is_tournament_bowler")
	search_fields = ("person__first_name", "person__last_name")
	list_filter = ("is_high_school_bowler", "is_league_bowler", "is_tournament_bowler")
