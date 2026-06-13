from django.contrib import admin

from openbowl.models import OpenBowlingActivity, OpenBowlingActivityGame


@admin.register(OpenBowlingActivity)
class OpenBowlingActivityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "sequence_number", "is_complete", "created_at")
    list_filter = ("is_complete",)


@admin.register(OpenBowlingActivityGame)
class OpenBowlingActivityGameAdmin(admin.ModelAdmin):
    list_display = ("id", "activity", "player", "game", "sort_order", "created_at")
    list_filter = ("activity",)
