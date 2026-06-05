from django.contrib import admin
from .models import HighSchool


@admin.register(HighSchool)
class HighSchoolAdmin(admin.ModelAdmin):
	list_display = ("school_name", "school_mascot", "address")
	search_fields = ("school_name", "school_mascot", "address__street1", "address__city__city")
	list_filter = ("address__city__state",)
