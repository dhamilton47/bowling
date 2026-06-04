from django.contrib import admin
from .models import Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
	list_display = ("last_name", "first_name", "middle_name", "preferred_name", "suffix", "address")
	search_fields = ("first_name", "middle_name", "last_name", "preferred_name", "suffix")
	list_filter = ("suffix",)
