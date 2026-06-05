from django.contrib import admin

from student.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ("high_school", "year_in_school", "created_at", "updated_at")
	search_fields = ("high_school__school_name",)
	list_filter = ("year_in_school",)
