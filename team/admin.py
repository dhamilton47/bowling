from django.contrib import admin
from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
	list_display = ("team",)
	search_fields = ("team",)
	filter_horizontal = ("players",)
