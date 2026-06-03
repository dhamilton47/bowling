from ntpath import realpath

from django.db import models
from django.core.validators import RegexValidator

US_STATES = [
	("Alabama", "AL"),
	("Alaska", "AK"),
	("Arizona", "AZ"),
	("Arkansas", "AR"),
	("California", "CA"),
	("Colorado", "CO"),
	("Connecticut", "CT"),
	("Delaware", "DE"),
	("Florida", "FL"),
	("Georgia", "GA"),
	("Hawaii", "HI"),
	("Idaho", "ID"),
	("Illinois", "IL"),
	("Indiana", "IN"),
	("Iowa", "IA"),
	("Kansas", "KS"),
	("Kentucky", "KY"),
	("Louisiana", "LA"),
	("Maine", "ME"),
	("Maryland", "MD"),
	("Massachusetts", "MA"),
	("Michigan", "MI"),
	("Minnesota", "MN"),
	("Mississippi", "MS"),
	("Missouri", "MO"),
	("Montana", "MT"),
	("Nebraska", "NE"),
	("Nevada", "NV"),
	("New Hampshire", "NH"),
	("New Jersey", "NJ"),
	("New Mexico", "NM"),
	("New York", "NY"),
	("North Carolina", "NC"),
	("North Dakota", "ND"),
	("Ohio", "OH"),
	("Oklahoma", "OK"),
	("Oregon", "OR"),
	("Pennsylvania", "PA"),
	("Rhode Island", "RI"),
	("South Carolina", "SC"),
	("South Dakota", "SD"),
	("Tennessee", "TN"),
	("Texas", "TX"),
	("Utah", "UT"),
	("Vermont", "VT"),
	("Virginia", "VA"),
	("Washington", "WA"),
	("West Virginia", "WV"),
	("Wisconsin", "WI"),
	("Wyoming", "WY"),
]

STATE_NAME_CHOICES = [(name, name) for name, _ in US_STATES]
STATE_ABBR_CHOICES = [(abbr, abbr) for _, abbr in US_STATES]


class State(models.Model):
	state = models.CharField(
		max_length=25,
		choices=STATE_NAME_CHOICES,
		unique=True,
		verbose_name="State",
		help_text="Full state name",
	)
	state_abbr = models.CharField(
		max_length=2,
		choices=STATE_ABBR_CHOICES,
		unique=True,
		verbose_name="State Abbreviation",
		help_text="2 letter state abbreviation",
		validators=[
			RegexValidator(
				regex=r"^[A-Z]{2}$",
				message="State abbreviation must be 2 uppercase letters",
			)
		]
	)

	class Meta:
		verbose_name = "State"
		verbose_name_plural = "States"
		ordering = ["state"]

	def __str__(self) -> str:
		return f"{self.state_abbr} - {self.state}"


class City(models.Model):
	city = models.CharField(
		max_length=25,
		blank=True,
		default="",
		verbose_name="City",
		help_text="City name",
	)
	state = models.ForeignKey(
		State,
		on_delete=models.PROTECT,
		related_name="cities",
		verbose_name="State",
	)
	zip_code = models.CharField(
		max_length=10,
		blank=True,
		default="",
		verbose_name="ZIP Code",
		help_text="5-digit ZIP or ZIP+4 (e.g. 12345 or 12345-6789)",
		validators=[
			RegexValidator(
				regex=r"^\d{5}(-\d{4})?$",
				message="ZIP code must be in 12345 or 12345-6789 format",
			)
		],
	)

	class Meta:
		unique_together = ("city", "state", "zip_code")
		verbose_name = "Locality"
		verbose_name_plural = "Localities"
		ordering = ["city", "state__state"]
			  
	def __str__(self) -> str:
		txt = f"{self.city}" if self.city else ""
		state = f"{self.state.state_abbr}" if self.state else ""
		if txt and state:
			txt += f", {state}"
		if self.zip_code:
			txt += f" {self.zip_code}"
		return txt.strip()


class Address(models.Model):
	street1 = models.CharField(
		max_length=75,
		blank=True,
		default="",
		verbose_name="Street Address",
		help_text="Primary street address",
	)
	street2 = models.CharField(
		max_length=75,
		blank=True,
		default="",
		verbose_name="Suite/Apt/etc.",
	)
	city = models.ForeignKey(
		City,
		on_delete=models.PROTECT,
		blank=True,
		default="",
		related_name="addresses",
		verbose_name="City, State, ZIP",
	)

	class Meta:
		verbose_name = "Address"
		verbose_name_plural = "Addresses"
		ordering = ["city", "street1"]

	def __str__(self) -> str:
		if self.city:
			txt = ""
			if self.street1:
				txt = f"{self.street1}"
			if self.street2:
				if txt:
					txt += f", {self.street2}"
			locality = f"{self.city}"
			if txt and locality:
					txt += f", "
			txt += f"{locality}"
				
			return txt.strip()
		else:
				return ""

