from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from .models import Address, City, State


class StateAbbrFilter(SimpleListFilter):
	title = "state"
	parameter_name = "state_abbr"

	def lookups(self, request, model_admin):
		states = State.objects.order_by("state_abbr").values_list("state_abbr", "state")
		return [(abbr, f"{abbr} - {name}") for abbr, name in states]

	def queryset(self, request, queryset):
		value = self.value()
		if not value:
			return queryset
		model_name = queryset.model.__name__
		if model_name == "State":
			return queryset.filter(state_abbr=value)
		if model_name == "City":
			return queryset.filter(state__state_abbr=value)
		if model_name == "Address":
			return queryset.filter(city__state__state_abbr=value)
		return queryset


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
	list_display = ("state_abbr", "state")
	search_fields = ("state", "state_abbr")
	ordering = ("state",)
	list_filter = (StateAbbrFilter,)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
	list_display = ("city", "state", "zip_code")
	search_fields = ("city", "zip_code", "state__state", "state__state_abbr")
	ordering = ("city", "state__state")
	list_filter = (StateAbbrFilter,)
	list_select_related = ("state",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
	list_display = ("street1", "street2", "city")
	search_fields = (
		"street1",
		"street2",
		"city__city",
		"city__zip_code",
		"city__state__state",
		"city__state__state_abbr",
	)
	ordering = ("city__state__state", "city__city", "street1")
	list_filter = (StateAbbrFilter,)
	list_select_related = ("city", "city__state")
