from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.progress.models import UserProgress

from .models import Book, Language
from .serializers import (
    BookDetailSerializer,
    BookListSerializer,
    LanguageSerializer,
)


def user_language_percents(user):
    """Average percent across ALL books of each language (missing books = 0)."""
    totals = {
        row["language_id"]: row["total"]
        for row in Book.objects.values("language_id").annotate(total=Count("id"))
    }
    sums = {
        row["book__language_id"]: row["sum"]
        for row in UserProgress.objects.filter(user=user)
        .values("book__language_id")
        .annotate(sum=Sum("percent_complete"))
    }
    return {lang: round((sums.get(lang, 0) / total), 1) for lang, total in totals.items()}


def user_book_percents(user):
    return {
        row["book_id"]: round(row["percent_complete"], 1)
        for row in UserProgress.objects.filter(user=user).values("book_id", "percent_complete")
    }


class LanguageListView(APIView):
    def get(self, request):
        percents = user_language_percents(request.user)
        languages = Language.objects.all()
        serializer = LanguageSerializer(
            languages, many=True, context={"request": request, "percents": percents}
        )
        return Response(serializer.data)


class LanguageBooksView(APIView):
    def get(self, request, pk):
        language = get_object_or_404(Language, pk=pk)
        books = Book.objects.filter(language=language)
        percents = user_book_percents(request.user)
        lang_data = LanguageSerializer(
            language, context={"request": request, "percents": percents}
        ).data
        lang_data["books"] = BookListSerializer(
            books, many=True, context={"request": request, "book_percents": percents}
        ).data
        return Response(lang_data)


class BookDetailView(APIView):
    def get(self, request, pk):
        book = get_object_or_404(Book.objects.select_related("language"), pk=pk)
        progress = UserProgress.objects.filter(user=request.user, book=book).first()
        serializer = BookDetailSerializer(
            book, context={"request": request, "progress": progress}
        )
        return Response(serializer.data)
