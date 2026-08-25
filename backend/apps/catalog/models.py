from django.db import models


class Language(models.Model):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    cover_image_url = models.CharField(max_length=300, blank=True, default="")
    order_index = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["order_index"]

    def __str__(self):
        return self.name


class Book(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name="books")
    topic = models.CharField(max_length=150)
    emoji = models.CharField(max_length=8, blank=True, default="")
    cover_image_url = models.CharField(max_length=300, blank=True, default="")
    order_index = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["order_index"]
        constraints = [
            models.UniqueConstraint(fields=["language", "order_index"], name="uniq_book_order")
        ]

    def __str__(self):
        return f"{self.language.code}:{self.topic}"


class BookSection(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="sections")
    order_index = models.PositiveIntegerField(default=0)
    original_text = models.TextField()
    translated_text = models.TextField()
    sentences = models.JSONField(default=list)
    translated_sentences = models.JSONField(default=list)
    audio = models.FileField(upload_to="audio", null=True, blank=True)
    timestamps = models.JSONField(default=list)

    class Meta:
        ordering = ["order_index"]
        constraints = [
            models.UniqueConstraint(fields=["book", "order_index"], name="uniq_section_order")
        ]

    def __str__(self):
        return f"section {self.order_index} of {self.book_id}"
