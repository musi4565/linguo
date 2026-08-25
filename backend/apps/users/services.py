from django.utils import timezone

from apps.achievements.models import Achievement, UserAchievement

from .models import User


def build_profile_payload(user: User) -> dict:
    from apps.progress.models import DailyActivity, UserProgress

    now = timezone.localtime()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    month_rows = DailyActivity.objects.filter(user=user, date__gte=month_start.date())
    month_minutes = round(sum(r.minutes_spent for r in month_rows))
    month_words = sum(r.words_learned_count for r in month_rows)
    active_days = month_rows.filter(minutes_spent__gte=1).count()
    completed = UserProgress.objects.filter(
        user=user, percent_complete__gte=99.9, last_accessed_at__gte=month_start
    ).count()

    achievements = []
    earned_map = {
        ua.achievement_id: ua.earned_at
        for ua in UserAchievement.objects.filter(user=user).select_related("achievement")
    }
    for a in Achievement.objects.all():
        earned_at = earned_map.get(a.id)
        achievements.append(
            {
                "code": a.code,
                "title": a.title,
                "icon": a.icon,
                "condition_description": a.condition_description,
                "earned": earned_at is not None,
                "earned_at": earned_at.isoformat() if earned_at else None,
            }
        )

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat(),
        },
        "month": {
            "label": now.strftime("%B %Y"),
            "minutes_spent": month_minutes,
            "words_saved": month_words,
            "lessons_completed": completed,
            "active_days": active_days,
        },
        "streak": _current_streak(user),
        "achievements": achievements,
        "telegram_connected": bool(user.telegram_chat_id),
    }


def _current_streak(user) -> int:
    from apps.progress.services import compute_streak

    return compute_streak(user)
