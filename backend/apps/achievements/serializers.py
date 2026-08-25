from rest_framework import serializers

from .models import Achievement, UserAchievement


class AchievementSerializer(serializers.ModelSerializer):
    earned = serializers.SerializerMethodField()
    earned_at = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ["code", "title", "icon", "condition_description", "earned", "earned_at"]

    def get_earned(self, obj):
        return obj.code in self.context.get("earned_codes", set())

    def get_earned_at(self, obj):
        dates = self.context.get("earned_dates", {})
        return dates.get(obj.code)
