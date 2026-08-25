from django.conf import settings
from rest_framework import serializers

from .models import Book, BookSection, Language


def abs_media_url(path):
    if not path:
        return None
    return f"{settings.MEDIA_URL}{path}"


class LanguageSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    percent_complete = serializers.SerializerMethodField()

    class Meta:
        model = Language
        fields = [
            "id",
            "code",
            "name",
            "description",
            "cover_image_url",
            "is_featured",
            "percent_complete",
        ]

    def get_cover_image_url(self, obj):
        url = abs_media_url(obj.cover_image_url)
        request = self.context.get("request")
        return request.build_absolute_uri(url) if url else None

    def get_percent_complete(self, obj):
        return self.context.get("percents", {}).get(obj.id, 0)


class BookListSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    percent_complete = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "topic",
            "emoji",
            "cover_image_url",
            "is_featured",
            "order_index",
            "percent_complete",
        ]

    def get_cover_image_url(self, obj):
        url = abs_media_url(obj.cover_image_url)
        request = self.context.get("request")
        return request.build_absolute_uri(url) if url else None

    def get_percent_complete(self, obj):
        return round(self.context.get("book_percents", {}).get(obj.id, 0), 1)


class SectionSerializer(serializers.ModelSerializer):
    audio_url = serializers.SerializerMethodField()

    class Meta:
        model = BookSection
        fields = [
            "id",
            "order_index",
            "original_text",
            "translated_text",
            "sentences",
            "translated_sentences",
            "timestamps",
            "audio_url",
        ]

    def get_audio_url(self, obj):
        if not obj.audio:
            return None
        request = self.context.get("request")
        url = obj.audio.url
        return request.build_absolute_uri(url) if request else url


class BookDetailSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    language = serializers.SerializerMethodField()
    sections = SectionSerializer(many=True, read_only=True)
    last_section_id = serializers.SerializerMethodField()
    percent_complete = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "topic",
            "emoji",
            "cover_image_url",
            "is_featured",
            "language",
            "sections",
            "last_section_id",
            "percent_complete",
        ]

    def get_cover_image_url(self, obj):
        url = abs_media_url(obj.cover_image_url)
        request = self.context.get("request")
        return request.build_absolute_uri(url) if url else None

    def get_language(self, obj):
        return {"id": obj.language.id, "code": obj.language.code, "name": obj.language.name}

    def get_last_section_id(self, obj):
        progress = self.context.get("progress")
        return progress.section_id if progress else None

    def get_percent_complete(self, obj):
        progress = self.context.get("progress")
        return round(progress.percent_complete, 1) if progress else 0


def build_language_payload(language, percents):
    """Plain-dict variant for nesting inside other responses."""
    return {
        "id": language.id,
        "code": language.code,
        "name": language.name,
        "description": language.description,
        "cover_image_url": abs_media_url(language.cover_image_url),
    }


def build_book_payload(book, book_percents):
    return {
        "id": book.id,
        "topic": book.topic,
        "emoji": book.emoji,
        "cover_image_url": abs_media_url(book.cover_image_url),
        "is_featured": book.is_featured,
        "order_index": book.order_index,
        "percent_complete": round(book_percents.get(book.id, 0), 1),
    }
