from django.contrib import admin
from .models import Lanes


@admin.register(Lanes)
class LanesAdmin(admin.ModelAdmin):
	list_display = ("lanes", "address")
	search_fields = ("lanes", "address__street1", "address__city__city")
	list_filter = ("address__city__state",)
