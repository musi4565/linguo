from datetime import timedelta

from django.utils import timezone


def compute_streak(user):
    """Consecutive active days (>= 1 minute) ending today or yesterday."""
    dates = list(
        user.daily_activities.filter(minutes_spent__gte=1)
        .values_list("date", flat=True)
        .order_by("-date")[:400]
    )
    if not dates:
        return 0
    today = timezone.localdate()
    start = None
    if dates[0] == today:
        start = today
    elif dates[0] == today - timedelta(days=1):
        start = dates[0]
    else:
        return 0
    date_set = set(dates)
    streak = 0
    d = start
    while d in date_set:
        streak += 1
        d -= timedelta(days=1)
    return streak
