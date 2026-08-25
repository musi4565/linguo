from django.urls import path

from .views import (
    LogSessionView,
    ProgressSaveView,
    ProgressSummaryView,
    StatsByLanguageView,
    StatsDailyView,
    StatsWeeklyView,
)

urlpatterns = [
    path("progress/", ProgressSaveView.as_view()),
    path("progress/summary/", ProgressSummaryView.as_view()),
    path("stats/daily/", StatsDailyView.as_view()),
    path("stats/weekly/", StatsWeeklyView.as_view()),
    path("stats/by-language/", StatsByLanguageView.as_view()),
    path("stats/log-session/", LogSessionView.as_view()),
]
