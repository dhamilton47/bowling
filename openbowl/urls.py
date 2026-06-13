from django.urls import path

from openbowl import views

app_name = "openbowl"

urlpatterns = [
    path("", views.open_bowling_home, name="open_bowling_home"),
    path(
        "activity/<int:activity_id>/",
        views.open_bowling_activity,
        name="open_bowling_activity",
    ),
    path(
        "activity/<int:activity_id>/player/<int:player_pk>/",
        views.open_bowling_activity,
        name="open_bowling_activity",
    ),
]
