import json
import random
import re
import time
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand
from django.db import close_old_connections
from django.utils import timezone

from apps.bookmarks.models import SavedWord
from apps.catalog.models import Book, Language
from apps.progress.models import DailyActivity
from apps.users.models import User

from django.conf import settings

API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
QUIZ_SIZE = 5
MIXED_SIZE = 10

FLAGS = {"en": "🇬🇧", "ru": "🇷🇺", "ar": "🇸🇦", "ko": "🇰🇷", "tr": "🇹🇷"}

CMD_LIST = (
    "/stat — natijalaringiz 📊\n"
    "/soz — barcha saqlangan so'zlaringiz 📖\n"
    "/test — til tanlab mini-test 🧪\n"
    "/help — yordam"
)

HELP = "👋 LINGUO botiga xush kelibsiz!\n\nBuyruqlar:\n" + CMD_LIST


def api_call(method, **payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API}/{method}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=35) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        api_call("sendMessage", **payload)
    except Exception as exc:
        print(f"[send xato] chat={chat_id}: {exc}")


def answer_callback(callback_id, text=None):
    payload = {"callback_query_id": callback_id}
    if text:
        payload["text"] = text
    try:
        api_call("answerCallbackQuery", **payload)
    except Exception:
        pass


def find_user_by_chat(chat_id):
    return User.objects.filter(telegram_chat_id=str(chat_id)).first()


def lang_info(lang_id):
    from apps.catalog.models import Language as Lang

    for l in Lang.objects.all():
        if l.id == lang_id:
            return l.name
    return "??"


def lang_flag_by_id(lang_id):
    from apps.catalog.models import Language as Lang

    for l in Lang.objects.all():
        if l.id == lang_id:
            return FLAGS.get(l.code, "🌐")
    return "🌐"


def lang_flag_by_code(code):
    return FLAGS.get(code, "🌐")


def language_percents(user):
    from django.db.models import Count, Sum

    totals = {
        row["language_id"]: row["total"]
        for row in Book.objects.values("language_id").annotate(total=Count("id"))
    }
    sums = {
        row["book__language_id"]: row["sum"]
        for row in user.progresses.values("book__language_id").annotate(sum=Sum("percent_complete"))
    }
    lines = []
    for lang_id, total in sorted(totals.items()):
        percent = round((sums.get(lang_id, 0) or 0) / total, 1)
        lines.append(f"  {lang_flag_by_id(lang_id)} {lang_info(lang_id)}: {percent}%")
    return "\n".join(lines)


ALL_LANGS = list(Language.objects.all()) if False else None


def get_all_langs():
    return list(Language.objects.all().order_by("id"))


class Command(BaseCommand):
    help = "LINGUO Telegram boti (long polling, stdlib)"

    def handle(self, *args, **options):
        self.stdout.write("Bot ishga tushdi... (to'xtatish uchun Ctrl+C)")
        offset = None
        ctx = {"quizzes": {}, "pending": {}}
        while True:
            try:
                close_old_connections()
                params = {"timeout": 25}
                if offset is not None:
                    params["offset"] = offset
                url = f"{API}/getUpdates?{urllib.parse.urlencode(params)}"
                with urllib.request.urlopen(url, timeout=35) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                for upd in data.get("result", []):
                    offset = upd["update_id"] + 1
                    cb = upd.get("callback_query")
                    if cb:
                        self.handle_callback(cb, ctx)
                        continue
                    msg = upd.get("message") or {}
                    chat_id = (msg.get("chat") or {}).get("id")
                    text = (msg.get("text") or "").strip()
                    if chat_id and text:
                        self.handle_message(chat_id, text, ctx)
            except KeyboardInterrupt:
                self.stdout.write("Bot to'xtatildi.")
                return
            except Exception as exc:
                print(f"[poll xato] {exc}")
                time.sleep(3)

    def handle_callback(self, cb, ctx):
        chat_id = cb["message"]["chat"]["id"]
        data = cb.get("data", "")
        callback_id = cb["id"]
        user = find_user_by_chat(chat_id)
        if not user:
            answer_callback(callback_id, "Avval akkauntni bog'lang.")
            return

        if data.startswith("quiz_"):
            ctx["pending"].pop(chat_id, None)
            answer_callback(callback_id)
            lang_code = data[5:]
            if lang_code == "mix":
                self.begin_quiz(chat_id, user, ctx, "mixed", None)
            else:
                lang = Language.objects.filter(code=lang_code).first()
                if not lang:
                    send(chat_id, "⚠️ Til topilmadi.")
                    return
                count = SavedWord.objects.filter(user=user, language=lang).count()
                if count == 0:
                    send(
                        chat_id,
                        f"{FLAGS.get(lang_code, '🌐')} {lang.name}\n\n"
                        f"Bu tilda hali so'z saqlanmagan.\n"
                        "Saytda kitob o'qib, shu tildan so'z saqlang!",
                    )
                    return
                if count < 4:
                    send(
                        chat_id,
                        f"{FLAGS.get(lang_code, '🌐')} {lang.name} — {count} ta so'z\n\n"
                        f"Test uchun kamida 4 ta so'z kerak.\n"
                        "Ko'proq so'z saqlang!",
                    )
                    return
                self.begin_quiz(chat_id, user, ctx, "lang", lang.id)

    def handle_message(self, chat_id, text, ctx):
        quizzes = ctx["quizzes"]
        user = find_user_by_chat(chat_id)

        m = re.match(r"^/start\s+(\S+)$", text)
        if m:
            code = m.group(1)
            candidate = User.objects.filter(telegram_link_code=code).first()
            ctx["pending"].pop(chat_id, None)
            if candidate:
                candidate.telegram_chat_id = str(chat_id)
                candidate.telegram_link_code = ""
                candidate.save(update_fields=["telegram_chat_id", "telegram_link_code"])
                quizzes.pop(chat_id, None)
                send(
                    chat_id,
                    f"✅ Akkaunt bog'landi!\n\n"
                    f"Salom, {candidate.name}! Endi buyruqlar sizniki:\n\n"
                    + CMD_LIST,
                )
            else:
                send(chat_id, "⚠️ Kod topilmadi yoki eskirgan. Saytda Profildan yangi havola oling.")
            return

        if text == "/start":
            send(
                chat_id,
                HELP + "\n\n🔗 Akkauntni bog'lash: saytda Profil → «Telegram botga ulanish» tugmasini bosing.",
            )
            return

        if text in ("/help", "/yordam"):
            send(chat_id, HELP)
            return

        if not user:
            send(
                chat_id,
                "🔒 Avval akkauntingizni bog'lang: saytda Profil → «Telegram botga ulanish».",
            )
            return

        if text == "/stat":
            self.cmd_stat(chat_id, user)
            return

        if text == "/soz":
            self.cmd_soz(chat_id, user)
            return

        if text == "/test":
            self.cmd_test(chat_id, user, ctx)
            return

        quiz = quizzes.get(chat_id)
        if quiz:
            self.check_answer(chat_id, text, quizzes)
            return

        send(chat_id, "🤔 Tushunmadim.\n\n" + CMD_LIST)

    def cmd_stat(self, chat_id, user):
        today = timezone.localdate()
        activity = DailyActivity.objects.filter(user=user, date=today).first()
        words_today = activity.words_learned_count if activity else 0
        minutes_today = round(activity.minutes_spent if activity else 0)
        total_words = SavedWord.objects.filter(user=user).count()
        send(
            chat_id,
            f"📊 Sizning natijalaringiz:\n\n"
            f"  Bugun o'rganilgan so'z: {words_today} ta\n"
            f"  Bugungi vaqt: {minutes_today} daq\n"
            f"  Lug'atdagi so'zlar: {total_words} ta\n\n"
            f"Tillar bo'yicha progress:\n{language_percents(user)}\n\n"
            + CMD_LIST,
        )

    def cmd_soz(self, chat_id, user):
        words = list(SavedWord.objects.filter(user=user).select_related("language").order_by("language__name", "word"))
        if not words:
            send(chat_id, "📖 Lug'atingiz hali bo'sh.\nSaytda kitob o'qib, so'z saqlang!\n\n" + CMD_LIST)
            return
        by_lang = {}
        for w in words:
            by_lang.setdefault(w.language, []).append(w)
        lines = ["📚 Barcha saqlangan so'zlaringiz:\n"]
        for lang, wlist in sorted(by_lang.items(), key=lambda x: x[0].id):
            flag = FLAGS.get(lang.code, "🌐")
            lines.append(f"{flag} {lang.name} ({len(wlist)} ta):")
            for w in wlist:
                lines.append(f"  • {w.word} — {w.translation}")
            lines.append("")
        send(chat_id, "\n".join(lines).strip() + "\n\n" + CMD_LIST)

    def cmd_test(self, chat_id, user, ctx):
        all_words = list(SavedWord.objects.filter(user=user).select_related("language"))
        if not all_words:
            send(
                chat_id,
                "🧪 Test uchun avval so'z saqlang!\n\n" + CMD_LIST,
            )
            return

        by_lang = {}
        for w in all_words:
            by_lang.setdefault(w.language, []).append(w)

        buttons = []
        info_lines = []
        for lang in get_all_langs():
            count = len(by_lang.get(lang, []))
            flag = FLAGS.get(lang.code, "🌐")
            if count == 0:
                info_lines.append(f"  {flag} {lang.name} — so'z yo'q")
            elif count < 4:
                info_lines.append(f"  {flag} {lang.name} — {count} ta so'z (kamida 4 kerak)")
            else:
                info_lines.append(f"  {flag} {lang.name} — {count} ta so'z ✅")
            buttons.append([{"text": f"{flag} {lang.name} ({count})", "callback_data": f"quiz_{lang.code}"}])

        total = len(all_words)
        if total >= MIXED_SIZE:
            info_lines.append(f"\n  🔀 Aralash — {MIXED_SIZE} ta savol barcha tillardan ✅")
            buttons.append([{"text": f"🔀 Aralash ({MIXED_SIZE})", "callback_data": "quiz_mix"}])

        markup = {"inline_keyboard": buttons}
        send(
            chat_id,
            f"🧪 Qaysi tildan test olmoqchisiz?\n\n"
            + "\n".join(info_lines)
            + "\n\nTugmalardan birini bosing:",
            reply_markup=markup,
        )
        ctx["pending"].pop(chat_id, None)

    def begin_quiz(self, chat_id, user, ctx, kind, value):
        all_words = list(SavedWord.objects.filter(user=user))
        if kind == "lang":
            words = [w for w in all_words if w.language_id == value]
            if len(words) < 4:
                send(chat_id, "⚠️ Bu tilda yetarli so'z yo'q.\n\n" + CMD_LIST)
                return
            picked = random.sample(words, min(QUIZ_SIZE, len(words)))
            title = f"{lang_flag_by_id(value)} {lang_info(value)} testi"
        else:
            by_lang = {}
            for w in all_words:
                by_lang.setdefault(w.language_id, []).append(w)
            picked = []
            for ws in by_lang.values():
                random.shuffle(ws)
                picked.extend(ws[:2])
            random.shuffle(picked)
            picked = picked[:MIXED_SIZE]
            if len(picked) < 4:
                send(chat_id, "⚠️ Test uchun yetarli so'z yo'q.\n\n" + CMD_LIST)
                return
            title = "🔀 Aralash test"

        ctx["quizzes"][chat_id] = {"words": picked, "idx": 0, "score": 0, "total": len(picked)}
        send(chat_id, f"🧪 {title} boshlandi! {len(picked)} ta savol.\nJavob: A / B / C / D")
        self.ask_question(chat_id, ctx["quizzes"])

    def ask_question(self, chat_id, quizzes):
        quiz = quizzes[chat_id]
        if quiz["idx"] >= quiz["total"]:
            self.finish_quiz(chat_id, quizzes)
            return
        word = quiz["words"][quiz["idx"]]
        seen = {word.translation}
        others = []
        same_lang = list(
            SavedWord.objects.filter(language_id=word.language_id)
            .exclude(id=word.id)
            .order_by("?")[:60]
        )
        any_lang = list(SavedWord.objects.exclude(id=word.id).order_by("?")[:40])
        for w in [*same_lang, *any_lang]:
            if w.translation not in seen:
                seen.add(w.translation)
                others.append(w.translation)
            if len(others) == 3:
                break
        options = [word.translation] + others
        while len(options) < 4:
            options.append(f"tarjima {len(options)}")
        random.shuffle(options)
        quiz["options"] = options
        letters = ["A", "B", "C", "D"]
        body = "\n".join(f"  {letters[i]}) {opt}" for i, opt in enumerate(options))
        send(chat_id, f"Savol {quiz['idx'] + 1}/{quiz['total']}\n\n❓ {word.word} = ?\n\n{body}")

    def finish_quiz(self, chat_id, quizzes):
        quiz = quizzes[chat_id]
        score = quiz["score"]
        total = quiz["total"]
        pct = round(score / total * 100) if total else 0
        if score == total:
            mark = "🏆 Mukammal! Barchasini to'g'ri javob berdingiz!"
        elif pct >= 70:
            mark = "🎉 Zo'r! Yaxshi natija!"
        elif pct >= 40:
            mark = "👍 Yaxshi! Davom eting!"
        else:
            mark = "💪 Mashq qilavering, yaxshilanasiz!"
        send(
            chat_id,
            f"🏁 Test tugadi!\n\n"
            f"📊 Natija: {score}/{total} ({pct}%)\n"
            f"{mark}\n\n"
            f"Qaytadan: /test\n\n"
            + CMD_LIST,
        )
        quizzes.pop(chat_id, None)

    def check_answer(self, chat_id, text, quizzes):
        quiz = quizzes.get(chat_id)
        if not quiz:
            return
        answer = text.strip().upper()[:1]
        if answer not in ("A", "B", "C", "D"):
            send(chat_id, "Iltimos, faqat A, B, C yoki D deb javob bering.")
            return
        letters = ["A", "B", "C", "D"]
        correct_idx = quiz["options"].index(quiz["words"][quiz["idx"]].translation)
        if answer == letters[correct_idx]:
            quiz["score"] += 1
            send(chat_id, "✅ To'g'ri!")
        else:
            send(
                chat_id,
                f"❌ Xato. To'g'ri javob: {letters[correct_idx]}) "
                f"{quiz['words'][quiz['idx']].translation}",
            )
        quiz["idx"] += 1
        self.ask_question(chat_id, quizzes)
