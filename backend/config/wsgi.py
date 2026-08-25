import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def _auto_seed():
    try:
        from django.core.management import call_command
        call_command("seed_content", verbosity=0)
    except Exception:
        pass


_auto_seed()

application = get_wsgi_application()
