import asyncio
import os

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

import edge_tts

from apps.catalog.models import BookSection, Language

VOICES = {
    "en": "en-US-BrianNeural",
    "ru": "ru-RU-DmitryNeural",
    "ar": "ar-SA-HamedNeural",
    "ko": "ko-KR-InJoonNeural",
    "tr": "tr-TR-AhmetNeural",
}

BITRATE = 48000
PAUSE_BETWEEN_REQUESTS = 0.2
MAX_RETRIES = 4


async def synth(text: str, voice: str) -> bytes:
    communicate = edge_tts.Communicate(text, voice, rate="-15%")
    data = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            data.extend(chunk["data"])
    return bytes(data)


async def synth_with_retry(text, voice):
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = await synth(text, voice)
            if raw:
                return raw
            last_exc = RuntimeError("bo'sh audio")
        except Exception as exc:
            last_exc = exc
        await asyncio.sleep(1.2 * attempt)
    raise RuntimeError(f"edge-tts xatosi ({voice}): {last_exc}")


def estimate_duration(raw: bytes) -> float:
    """CBR mp3 (48 kbps) uchun davomiylikni bayt hajmidan hisoblash."""
    return len(raw) * 8.0 / BITRATE


async def process_section(section: BookSection, voice: str, force: bool) -> bool:
    if not section.sentences:
        return False
    if section.audio and not force and section.timestamps:
        return False

    parts = []
    timestamps = []
    cursor = 0.0
    for sentence in section.sentences:
        raw = await synth_with_retry(sentence, voice)
        duration = estimate_duration(raw)
        timestamps.append(
            {"text": sentence, "start": round(cursor, 2), "end": round(cursor + duration, 2)}
        )
        cursor += duration
        parts.append(raw)
        await asyncio.sleep(PAUSE_BETWEEN_REQUESTS)

    mp3 = b"".join(parts)
    filename = f"{section.book.language.code}/book{section.book_id}_s{section.order_index}.mp3"
    section.audio.save(filename, ContentFile(mp3), save=False)
    section.timestamps = timestamps
    section.save(update_fields=["audio", "timestamps"])
    return True


def pending_sections(language):
    """Audio yoki timestamp'i yetishmaydigan bo'limlar."""
    sections = [
        s
        for s in BookSection.objects.filter(book__language=language).select_related(
            "book", "book__language"
        )
        if not s.audio or not s.timestamps
    ]
    sections.sort(key=lambda s: (s.book.order_index, s.order_index))
    return sections


async def run(language_code, force, limit, offset, concurrency):
    jobs = []
    languages = Language.objects.all()
    if language_code:
        languages = languages.filter(code=language_code)

    for language in languages:
        voice = VOICES.get(language.code)
        if not voice:
            raise RuntimeError(f"'{language.code}' tili uchun ovoz topilmadi")
        sections = pending_sections(language)
        if offset:
            sections = sections[offset:]
        if limit:
            sections = sections[:limit]
        total = len(sections)
        for idx, section in enumerate(sections, 1):
            jobs.append((idx, total, section, voice))

    sem = asyncio.Semaphore(concurrency)

    async def worker(job):
        idx, total, section, voice = job
        code = section.book.language.code
        tag = f"[{code}] bo'lim {idx}/{total} (book{section.book_id}_s{section.order_index})"
        async with sem:
            try:
                created = await process_section(section, voice, force)
                print(f"{tag}: tayyor" if created else f"{tag}: o'tkazildi", flush=True)
                return "done" if created else "skipped"
            except Exception as exc:
                print(f"XATO {tag}: {exc}", flush=True)
                return "failed"

    results = await asyncio.gather(*(worker(j) for j in jobs))
    done = results.count("done")
    skipped = results.count("skipped")
    failed = results.count("failed")
    print(f"\nYakuni: {done} yaratildi, {skipped} o'tkazildi, {failed} xato.", flush=True)


class Command(BaseCommand):
    help = (
        "Bo'lim matnlari uchun edge-tts orqali MP3 + timestamp'lar generatsiya qiladi "
        "(standart: 5 ta bo'lim parallel)"
    )

    def add_arguments(self, parser):
        parser.add_argument("--language", type=str, default=None, help="Faqat shu til kodi (en/ru/ar/ko/tr)")
        parser.add_argument("--force", action="store_true", help="Mavjud audiolarni ham qayta yaratish")
        parser.add_argument("--limit", type=int, default=None, help="Bo'limlar sonini cheklash (test uchun)")
        parser.add_argument("--offset", type=int, default=None, help="Birinchi N ta kutayotgan bo'limni tashlab ketish")
        parser.add_argument("--concurrency", type=int, default=5, help="Bir vaqtda ishlanadigan bo'limlar soni")

    def handle(self, *args, **options):
        asyncio.run(
            run(
                options["language"],
                options["force"],
                options["limit"],
                options["offset"],
                options["concurrency"],
            )
        )
