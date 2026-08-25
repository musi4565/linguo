from django.urls import path

from .views import AchievementsListView

urlpatterns = [
    path("achievements/", AchievementsListView.as_view()),
]
