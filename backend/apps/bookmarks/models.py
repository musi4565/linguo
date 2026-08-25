from django.db import models

from apps.catalog.models import Book, Language
from config.settings import AUTH_USER_MODEL


class Bookmark(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "book"], name="uniq_user_bookmark")
        ]

    def __str__(self):
        return f"{self.user_id} → {self.book_id}"


class SavedWord(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_words")
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="saved_words")
    word = models.CharField(max_length=200)
    translation = models.CharField(max_length=200)
    source_book = models.ForeignKey(
        Book, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.word} → {self.translation}"
