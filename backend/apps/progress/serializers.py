from rest_framework import serializers

from .models import DailyActivity, LanguageActivity, UserProgress


class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = ["id", "book", "section", "percent_complete", "last_accessed_at"]


class ProgressSaveSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    section_id = serializers.IntegerField(required=False, allow_null=True)
    percent = serializers.FloatField(min_value=0, max_value=100)


class LogSessionSerializer(serializers.Serializer):
    minutes = serializers.IntegerField(min_value=1, max_value=180)
    language_id = serializers.IntegerField(required=False, allow_null=True)


class DailyActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyActivity
        fields = ["date", "minutes_spent", "words_learned_count"]
