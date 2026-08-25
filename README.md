# LINGUO — Fullstack til o'rganish platformasi

Chet tillarni **muddatsiz, bosimsiz, o'z tezligida** o'rganish uchun veb-platforma.
Kitob o'qish orqali: bir tomonda original til, ikkinchi tomonda o'zbekcha tarjima + audio ovozli o'qish.

## Texnologiyalar

| Qism | Stack |
|---|---|
| Backend | Django 6 + Django REST Framework + SimpleJWT |
| Baza | PostgreSQL (localhost:5433) |
| Audio | edge-tts (Microsoft Neural voices) — MP3 + gap-darajasidagi timestamp'lar |
| Frontend | Vite + React 19 + react-router-dom + axios + zustand |
| Styling | Oddiy CSS (glassmorphism, blob animatsiyalar, brand-gradient) |

## Loyiha tuzilishi

```
LINGUO/
├── backend/
│   ├── config/            # settings, urls
│   ├── apps/
│   │   ├── users/         # CustomUser, auth (JWT), profil endpointlari
│   │   ├── catalog/       # Language, Book, BookSection (+ seed/generate_audio commandlari)
│   │   ├── progress/      # UserProgress, DailyActivity, statistika
│   │   ├── bookmarks/     # Bookmark, SavedWord
│   │   └── achievements/  # yutuqlar tizimi
│   └── media/             # audio/*.mp3 va covers/*.svg
└── frontend/              # Vite + React SPA
    └── src/{api,store,components,pages,styles}
```

## Ishga tushirish

### 1. Backend

```powershell
cd backend
python -m venv .venv                      # birinchi marta
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python bootstrap_db.py      # linguo bazasi+useri yaratadi (birinchi marta)
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py seed_content        # 5 til × 10 kitob × 4 bo'lim + SVG coverlar
.venv\Scripts\python manage.py generate_audio --language en   # audiolarni generatsiya qilish
.venv\Scripts\python manage.py runserver 127.0.0.1:8001
```

DB kredensialari `config/settings.py`da: `linguo / linguo_dev_2026 @ localhost:5433`.

> **Eslatma:** 8000-port boshqa loyihaga band bo'lgani uchun backend **8001**-portda ishlaydi.
> Audio mavjud bo'lsa qayta generatsiya shart emas (`media/audio/` saqlanib qoladi).

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev          # http://localhost:5188
```

Birinchi ochilish → `/onboarding` → Login sahifasidan ro'yxatdan o'ting.

## Asosiy imkoniyatlar

- **Onboarding** (2 slayd) → **Login/Ro'yxatdan o'tish** (JWT: access 30 daq / refresh 7 kun)
- **Asosiy**: gradient banner + 5 ta til kartochkasi ("Top tanlov" badge bilan)
- **Kurslarim** (3 bosqich): tillar (progress %) → 10 ta kitob setkasi → O'qish rejimi
- **Reader**: `1fr 1px 1fr` grid (divider alohida ustun), audio pleer (`timeupdate` bilan joriy gap highlight), tezlik (1x/1.25x/1.5x), har 60 s sessiya log'i, progress saqlanadi
- **Xatcho'p**: Darslar / So'zlar tab'lari (o'chirish bilan)
- **Statistika**: streak, so'z/dars/jami vaqt metrikalari, haftalik bar-grafik, conic-gradient maqsad doirasi, tillar taqsimoti
- **Profil**: ⚙️ modal (ism/parol o'zgartirish, chiqish), oylik natijalar, yutuq badge'lari

## API xulosa

`POST /api/auth/register|login|refresh|logout` · `GET /api/languages` ·
`GET /api/languages/:id/books` · `GET /api/books/:id` · `POST /api/progress` ·
`GET /api/progress/summary` · `GET|POST|DELETE /api/bookmarks[/:id]` ·
`GET|POST|DELETE /api/saved-words[/:id]` · `GET /api/stats/daily|weekly|by-language` ·
`POST /api/stats/log-session` · `GET|PATCH /api/profile` · `PATCH /api/profile/password` ·
`GET /api/achievements`

To'liq E2E tekshiruv: `powershell -ExecutionPolicy Bypass -File backend\smoke_test.ps1`
(buning uchun backend ishlab turishi kerak).

## Xavfsizlik

- Parollar Django `set_password` (PBKDF2) bilan hash'lanadi
- JWT throttling: auth endpointlar 60/soat
- Har foydalanuvchi faqat o'z resurslariga kira oladi (`user_id` JWT'dan)
- Refresh token rotatsiya + blacklist (logout)

