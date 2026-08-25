from django.db import models

from apps.catalog.models import Book, BookSection, Language
from config.settings import AUTH_USER_MODEL


class UserProgress(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progresses")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="user_progresses")
    section = models.ForeignKey(
        BookSection, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    percent_complete = models.FloatField(default=0)
    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "book"], name="uniq_user_book_progress")
        ]

    def __str__(self):
        return f"{self.user_id}:{self.book_id}:{self.percent_complete}%"


class DailyActivity(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_activities")
    date = models.DateField()
    minutes_spent = models.FloatField(default=0)
    words_learned_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="uniq_user_day_activity")
        ]


class LanguageActivity(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="language_activities")
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="user_activities")
    minutes_spent = models.FloatField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "language"], name="uniq_user_lang_time")
        ]
