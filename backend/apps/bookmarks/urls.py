from django.urls import path

from .views import (
    BookmarkDeleteView,
    BookmarkListCreateView,
    SavedWordDeleteView,
    SavedWordListCreateView,
    WordTranslateView,
)

urlpatterns = [
    path("bookmarks/", BookmarkListCreateView.as_view()),
    path("bookmarks/<int:pk>/", BookmarkDeleteView.as_view()),
    path("saved-words/", SavedWordListCreateView.as_view()),
    path("saved-words/<int:pk>/", SavedWordDeleteView.as_view()),
    path("translate-word/", WordTranslateView.as_view()),
]
