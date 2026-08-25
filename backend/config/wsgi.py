import os
import threading

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def _auto_seed():
    try:
        from django.core.management import call_command
        call_command("seed_content", verbosity=0)
    except Exception:
        pass


def _start_bot():
    try:
        from apps.users.management.commands.runbot import Command
        cmd = Command()
        cmd.handle()
    except Exception as exc:
        print(f"[bot xato] {exc}")


_auto_seed()

if os.environ.get("RUN_BOT", "true").lower() == "true":
    t = threading.Thread(target=_start_bot, daemon=True)
    t.start()
    print("[bot] Telegram bot background thread started")

application = get_wsgi_application()
