from datetime import timedelta

from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.achievements.services import check_achievements
from apps.bookmarks.models import SavedWord
from apps.catalog.models import Book, Language
from config import settings

from .models import DailyActivity, LanguageActivity, UserProgress
from .serializers import (
    DailyActivitySerializer,
    LogSessionSerializer,
    ProgressSaveSerializer,
    UserProgressSerializer,
)
from .services import compute_streak


class ProgressSaveView(APIView):
    def post(self, request):
        serializer = ProgressSaveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        book = get_object_or_404(Book, pk=data["book_id"])
        progress, _ = UserProgress.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={
                "section_id": data.get("section_id"),
                "percent_complete": data["percent"],
            },
        )
        check_achievements(request.user)
        return Response(UserProgressSerializer(progress).data, status=201)


class ProgressSummaryView(APIView):
    def get(self, request):
        lang_rows = (
            UserProgress.objects.filter(user=request.user)
            .values("book__language_id")
            .annotate(sum_percent=Sum("percent_complete"))
        )
        sums = {r["book__language_id"]: r["sum_percent"] for r in lang_rows}
        totals = {
            row["language_id"]: row["total"]
            for row in Book.objects.values("language_id").annotate(total=Count("id"))
        }
        result = []
        overall_sum = 0.0
        overall_total_books = 0
        for lang in Language.objects.all():
            total_books = totals.get(lang.id, 0)
            percent = round(sums.get(lang.id, 0) / total_books, 1) if total_books else 0.0
            result.append(
                {
                    "language_id": lang.id,
                    "code": lang.code,
                    "name": lang.name,
                    "percent": percent,
                }
            )
            overall_sum += sums.get(lang.id, 0)
            overall_total_books += total_books
        overall = round(overall_sum / overall_total_books, 1) if overall_total_books else 0.0
        return Response({"overall_percent": overall, "languages": result})


class StatsDailyView(APIView):
    def get(self, request):
        today = timezone.localdate()
        start = today - timedelta(days=29)
        rows = DailyActivity.objects.filter(user=request.user, date__gte=start).order_by("date")
        completed = UserProgress.objects.filter(
            user=request.user, percent_complete__gte=99.9
        ).aggregate(c=Count("id"))
        total_minutes_row = DailyActivity.objects.filter(user=request.user).aggregate(
            m=Sum("minutes_spent")
        )
        payload = {
            "streak": compute_streak(request.user),
            "total_minutes": round(total_minutes_row["m"] or 0),
            "words_learned": SavedWord.objects.filter(user=request.user).count(),
            "lessons_completed": completed["c"] or 0,
            "daily_goal_minutes": settings.DAILY_GOAL_MINUTES,
            "days": DailyActivitySerializer(rows, many=True).data,
        }
        return Response(payload)


class StatsWeeklyView(APIView):
    def get(self, request):
        today = timezone.localdate()
        days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        rows = {
            r.date: round(r.minutes_spent)
            for r in DailyActivity.objects.filter(user=request.user, date__gte=days[0])
        }
        week = [{"date": d.isoformat(), "minutes": rows.get(d, 0)} for d in days]
        return Response(
            {
                "week": week,
                "today": week[-1],
                "today_minutes": week[-1]["minutes"],
                "daily_goal_minutes": settings.DAILY_GOAL_MINUTES,
            }
        )


class StatsByLanguageView(APIView):
    def get(self, request):
        times = {
            row.language_id: row.minutes_spent
            for row in LanguageActivity.objects.filter(user=request.user)
        }
        total = sum(times.values())
        result = []
        for lang in Language.objects.all():
            minutes = round(times.get(lang.id, 0))
            percent = round(minutes / total * 100, 1) if total else 0.0
            result.append(
                {
                    "language_id": lang.id,
                    "code": lang.code,
                    "name": lang.name,
                    "minutes": minutes,
                    "percent": percent,
                }
            )
        return Response({"total_minutes": round(total), "languages": result})


class LogSessionView(APIView):
    def post(self, request):
        serializer = LogSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        minutes = serializer.validated_data["minutes"]
        language_id = serializer.validated_data.get("language_id")

        today = timezone.localdate()
        activity, _ = DailyActivity.objects.get_or_create(user=request.user, date=today)
        activity.minutes_spent += minutes
        activity.save()

        if language_id:
            lang = get_object_or_404(Language, pk=language_id)
            la, _ = LanguageActivity.objects.get_or_create(user=request.user, language=lang)
            la.minutes_spent += minutes
            la.save()

        check_achievements(request.user)
        return Response(
            {"date": today.isoformat(), "minutes_spent": round(activity.minutes_spent)},
            status=201,
        )
