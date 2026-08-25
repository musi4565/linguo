from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)
    name = models.CharField(max_length=150)
    avatar_url = models.CharField(max_length=300, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    telegram_chat_id = models.CharField(max_length=32, blank=True, default="")
    telegram_link_code = models.CharField(max_length=40, blank=True, default="")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email
