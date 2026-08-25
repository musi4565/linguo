# LINGUO himoya nutqi (~2.5 daqiqa)

## 1-kirish (titul)
Assalomu alaykum. Men taqdimotimda **LINGUO** — chet tillarni o'qib va tinglab o'rganish platformasining muammosi va yechimi haqida gapirib beraman.

## 2-Muammo
Loyihani boshlashdan oldin uchta asosiy muammoga duch keldik:

Birinchisi — **audio va matn alohida-alohida**. O'quvchi audioni tinglaydi, lekin so'z matnda qayerda — bilmaydi; sinxronlik yo'q.

Ikkinchisi — **kontent tengsiz**. Barcha ilovalar deyarli faqat ingliz tiliga qaratilgan: rus, arab, koreys yoki turk tilini o'rganmoqchi bo'lsangiz, "matn + audio" birga keladigan sifatli material topib bo'lmaydi.

Uchinchisi — **so'zlar yodlanmaydi**. O'qish paytida uchragan noma'lum so'z lug'atga yozib olinmasa, u yo'qolib qoladi.

## 3-Yechim
Bizning yechimiz — bitta ekranda hammasi birga:

- Reader rejimida audio ijro etilganda **jumlalar ayni o'qilayotgan joyda ajralib turadi**, tezlikni 1x dan 1.5x gacha sozlash mumkin;
- Har bir til uchun **10 tadan kitob** — 1 bo'limli, ~5 minutlik darslar: original matn, o'zbekcha tarjima va professional ovozli audio;
- Eng qiziq qismi: matndagi **istalgan so'zga bosilsa** — avtomatik tarjima chiqadi va bitta tugma bilan shaxsiy lug'atga saqlanadi;
- Progress foizi, kunlik statistika va yutuqlar motivatsiyani saqlab turadi.

## 4-Texnologiya
Backend — Django REST + PostgreSQL + JWT avtorizatsiya; audio esa edge-tts xizmati orqali generatsiya qilinadi. Frontend — React 19, Vite va Zustand asosida qurilgan.

## 5-Test davomida topilgan muammo va yechimi
Sinov davomida ikkita katta kamchilik aniqladik:

**Birinchisi** — audio faqat ingliz tilida to'liq edi: rusda 7/10, arab, koreys va turk tillarida umuman yo'q edi. Buni edge-tts asosidagi **parallel generatsiya** bilan hal qildik: 33 bo'lim atigi **~10 daqiqada** tayyorlandi — oddiy ketma-ket usulda bu 8 soatdan ortiq vaqt olardi. Hozir 5 tilda ham kontent mutlaqo teng.

**Ikkinchisi** — "So'zlar" bo'limi bo'sh turar edi: backend tayyor, lekin interfeys yo'q edi. Reader'ga **bos-saqla mexanizmini** qo'shdik: Google va zaxira MyMemory tarjima xizmatlari ishlaydi, natija Xatchop bo'limida kartochka ko'rinishida saqlanadi va kerak bo'lsa o'chiriladi.

## 6-Demo
Endi jonli demo ko'rsataman: ro'yxatdan o'tish → kurslar → kitob ochish → audio sinxronini ko'rish → so'zni bosib saqlash → Xatchop'da tekshirish.

## 7-Yakun
Natijada — 5 til, 50 ta to'liq bo'lim, sinxron audio va shaxsiy lug'atli platforma tayyor. Kelajakda flashcard rejimi, offlayn versiya va mobil ilovani rejalashtirmoqdamiz. E'tiboringiz uchun rahmat!

---

### Eslatma (o'zingizga):
- Nutq taxminan **2 daqiqa 40 soniya** — agar qisqartirish kerak bo'lsa, "Texnologiya" bo'limini olib tashlang.
- Demo paytida brauzerda `/start` havolasidan boshlang, keshlangan sessiyadan chiqish uchun.
- Agar internet uzilsa, tarjima popup'i "avto-tarjima topilmadi" deydi — bu holda qo'lda yozib saqlashni ko'rsatsangiz, fallback ham ishlayotganini ko'rsatasiz (bu minus emas, afzallik!).
