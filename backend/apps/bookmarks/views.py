import json
import re
import urllib.parse
import urllib.request

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.achievements.services import check_achievements
from apps.catalog.models import Book, Language
from apps.progress.models import DailyActivity

from .models import Bookmark, SavedWord
from .serializers import (
    BookmarkCreateSerializer,
    BookmarkSerializer,
    SavedWordCreateSerializer,
    SavedWordSerializer,
    book_brief,
)


class BookmarkListCreateView(APIView):
    def get(self, request):
        bookmarks = Bookmark.objects.filter(user=request.user).select_related(
            "book", "book__language"
        )
        return Response(BookmarkSerializer(bookmarks, many=True).data)

    def post(self, request):
        serializer = BookmarkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = get_object_or_404(Book, pk=serializer.validated_data["book_id"])
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, book=book)
        return Response(
            {
                "detail": "Xatcho'pka qo'shildi." if created else "Allaqachon saqlangan.",
                "created": created,
                "bookmark": BookmarkSerializer(bookmark).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class BookmarkDeleteView(APIView):
    def delete(self, request, pk):
        bookmark = get_object_or_404(Bookmark, pk=pk, user=request.user)
        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SavedWordListCreateView(APIView):
    def get(self, request):
        words = SavedWord.objects.filter(user=request.user).select_related("language")
        return Response(SavedWordSerializer(words, many=True).data)

    def post(self, request):
        serializer = SavedWordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        lang = get_object_or_404(Language, pk=data["language_id"])
        source_book = None
        if data.get("source_book_id"):
            source_book = Book.objects.filter(pk=data["source_book_id"]).first()
        word = SavedWord.objects.create(
            user=request.user,
            language=lang,
            word=data["word"].strip(),
            translation=data["translation"].strip(),
            source_book=source_book,
        )
        from django.utils import timezone

        activity, _ = DailyActivity.objects.get_or_create(
            user=request.user, date=timezone.localdate()
        )
        activity.words_learned_count += 1
        activity.save()
        check_achievements(request.user)
        return Response(SavedWordSerializer(word).data, status=status.HTTP_201_CREATED)


class SavedWordDeleteView(APIView):
    def delete(self, request, pk):
        word = get_object_or_404(SavedWord, pk=pk, user=request.user)
        word.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WordTranslateView(APIView):
    """Bitta so'zni o'zbek tiliga avto-tarjima qiladi (Google gtx + MyMemory zaxira)."""

    TIMEOUT_SECONDS = 6

    def _fetch(self, url):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=self.TIMEOUT_SECONDS) as resp:
            return resp.read().decode("utf-8")

    def _google(self, word, source):
        url = (
            "https://translate.googleapis.com/translate_a/single?client=gtx&dt=t"
            f"&sl={urllib.parse.quote(source)}&tl=uz&q={urllib.parse.quote(word)}"
        )
        data = json.loads(self._fetch(url))
        parts = [block[0] for block in (data[0] or []) if block and block[0]]
        return " ".join(parts).strip() or None

    def _mymemory(self, word, source):
        url = (
            "https://api.mymemory.translated.net/get?"
            f"q={urllib.parse.quote(word)}&langpair={urllib.parse.quote(source)}|uz"
        )
        data = json.loads(self._fetch(url))
        text = (data.get("responseData") or {}).get("translatedText") or ""
        text = str(text).strip()
        if not text or text.upper() in ("MYMEMORY WARNING", "INVALID LANGUAGE PAIR SPECIFIED"):
            return None
        return text

    def get(self, request):
        raw = (request.query_params.get("word") or "").strip()
        source = (request.query_params.get("lang") or "en").strip().lower()
        if not raw:
            return Response({"translation": None})
        word = re.sub(r"[^\w'’-]+", "", raw, flags=re.UNICODE) or raw
        translation = None
        for fetcher in (self._google, self._mymemory):
            try:
                translation = fetcher(word, source)
            except Exception:
                translation = None
            if translation:
                break
        return Response({"translation": translation})
