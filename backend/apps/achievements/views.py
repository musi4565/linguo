from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Achievement, UserAchievement
from .serializers import AchievementSerializer


class AchievementsListView(APIView):
    def get(self, request):
        earned = UserAchievement.objects.filter(user=request.user).select_related("achievement")
        codes = set()
        dates = {}
        for ua in earned:
            codes.add(ua.achievement.code)
            dates[ua.achievement.code] = ua.earned_at.isoformat()
        achievements = Achievement.objects.all()
        serializer = AchievementSerializer(
            achievements, many=True, context={"earned_codes": codes, "earned_dates": dates}
        )
        return Response(serializer.data)
