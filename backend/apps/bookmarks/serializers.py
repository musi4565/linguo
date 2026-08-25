from rest_framework import serializers

from apps.catalog.serializers import abs_media_url

from .models import Bookmark, SavedWord


def book_brief(book):
    return {
        "id": book.id,
        "topic": book.topic,
        "emoji": book.emoji,
        "cover_image_url": abs_media_url(book.cover_image_url),
        "language": {"id": book.language.id, "code": book.language.code, "name": book.language.name},
    }


class BookmarkSerializer(serializers.ModelSerializer):
    book = serializers.SerializerMethodField()

    class Meta:
        model = Bookmark
        fields = ["id", "book", "created_at"]

    def get_book(self, obj):
        return book_brief(obj.book)


class SavedWordSerializer(serializers.ModelSerializer):
    language = serializers.SerializerMethodField()

    class Meta:
        model = SavedWord
        fields = ["id", "language", "word", "translation", "created_at"]

    def get_language(self, obj):
        return {"id": obj.language.id, "code": obj.language.code, "name": obj.language.name}


class BookmarkCreateSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()


class SavedWordCreateSerializer(serializers.Serializer):
    language_id = serializers.IntegerField()
    word = serializers.CharField(max_length=200)
    translation = serializers.CharField(max_length=200)
    source_book_id = serializers.IntegerField(required=False, allow_null=True)
