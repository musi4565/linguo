from django.urls import path

from .views import BookDetailView, LanguageBooksView, LanguageListView

urlpatterns = [
    path("languages/", LanguageListView.as_view()),
    path("languages/<int:pk>/books/", LanguageBooksView.as_view()),
    path("books/<int:pk>/", BookDetailView.as_view()),
]
