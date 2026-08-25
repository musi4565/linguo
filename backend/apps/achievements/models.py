from django.db import models

from config.settings import AUTH_USER_MODEL


class Achievement(models.Model):
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=150)
    icon = models.CharField(max_length=16, blank=True, default="")
    condition_description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.code


class UserAchievement(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name="holders")
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-earned_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "achievement"], name="uniq_user_achievement")
        ]
