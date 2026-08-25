from django.db.models import Count

from apps.bookmarks.models import SavedWord
from apps.progress.models import UserProgress
from apps.progress.services import compute_streak

from .models import Achievement, UserAchievement

ACHIEVEMENT_SEED = [
    ("first_lesson", "Birinchi qadam", "🚀", "Birinchi darsni boshlang"),
    ("streak_3", "Uch kunlik olov", "🔥", "3 kun ketma-ket mashq qiling"),
    ("streak_7", "Haftalik seriya", "⚡", "7 kun ketma-ket mashq qiling"),
    ("words_10", "So'z yig'uvchi", "📚", "10 ta so'z saqlang"),
    ("words_50", "Lug'at ustasi", "🏆", "50 ta so'z saqlang"),
    ("finisher", "Kitob bosib o'tuvchi", "🎯", "Butun kitobni tugallang"),
]


def check_achievements(user):
    streak = compute_streak(user)
    words = SavedWord.objects.filter(user=user).count()
    progress_count = UserProgress.objects.filter(user=user).count()
    completed_books = UserProgress.objects.filter(user=user, percent_complete__gte=99.9).count()

    conditions = {
        "first_lesson": progress_count >= 1,
        "streak_3": streak >= 3,
        "streak_7": streak >= 7,
        "words_10": words >= 10,
        "words_50": words >= 50,
        "finisher": completed_books >= 1,
    }

    granted = []
    for code, satisfied in conditions.items():
        if not satisfied:
            continue
        achievement = Achievement.objects.filter(code=code).first()
        if not achievement:
            continue
        _, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
        if created:
            granted.append(code)
    return granted
