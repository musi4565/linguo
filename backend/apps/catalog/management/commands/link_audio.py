import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.catalog.models import BookSection


class Command(BaseCommand):
    help = "Mavjud MP3 fayllarni DB audio field ga bog'laydi"

    def handle(self, *args, **options):
        audio_root = Path(settings.MEDIA_ROOT) / "audio"
        if not audio_root.exists():
            self.stderr.write(f"audio papka topilmadi: {audio_root}")
            return

        linked = 0
        for section in BookSection.objects.select_related("book__language").all():
            lang_code = section.book.language.code
            filename = f"book{section.book_id}_s{section.order_index}.mp3"
            mp3_path = audio_root / lang_code / filename
            if mp3_path.exists() and not section.audio:
                section.audio.name = f"audio/{lang_code}/{filename}"
                section.save(update_fields=["audio"])
                linked += 1

        self.stdout.write(f"{linked} ta audio bog'landi")
