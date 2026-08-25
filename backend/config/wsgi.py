import os
import threading

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


def _auto_seed():
    try:
        from django.core.management import call_command
        call_command("seed_content", verbosity=2)
        print("[seed] seed_content completed successfully")
    except Exception as exc:
        print(f"[seed] ERROR: {exc}")


def _start_bot():
    import django
    django.setup()
    try:
        from apps.users.management.commands.runbot import Command
        cmd = Command()
        cmd.handle()
    except Exception as exc:
        print(f"[bot xato] {exc}")


_auto_seed()


def _link_audio():
    try:
        from django.core.management import call_command
        call_command("link_audio", verbosity=1)
    except Exception as exc:
        print(f"[link_audio] ERROR: {exc}")


_link_audio()

if os.environ.get("RUN_BOT", "true").lower() == "true":
    t = threading.Thread(target=_start_bot, daemon=True)
    t.start()
    print("[bot] Telegram bot background thread started")
