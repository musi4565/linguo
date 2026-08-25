import os

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.achievements.models import Achievement
from apps.achievements.services import ACHIEVEMENT_SEED
from apps.catalog.models import Book, BookSection, Language

from .long_stories_a import LONG_STORIES_A
from .long_stories_b import LONG_STORIES_B
from .long_stories_c import LONG_STORIES_C
from .long_stories_d import LONG_STORIES_D
from .long_stories_e import LONG_STORIES_E
from .long_stories_f import LONG_STORIES_F
from .continuations import CONTINUATIONS

from .ls_ru_p1 import PART1 as RU_P1
from .ls_ru_p2 import PART2 as RU_P2
from .ls_ru_p3 import PART3 as RU_P3
from .ls_ru_cont import CONTRU
from .long_stories_ar import LONG_STORIES_AR
from .continuations_ar import CONTINUATIONS_AR
from .long_stories_tr import LONG_STORIES_TR
from .continuations_tr import CONTINUATIONS_TR
from .long_stories_ko import LONG_STORIES_KO
from .continuations_ko import CONTINUATIONS_KO


def _build_story_set(base_parts, continuations):
    merged = {}
    for part in base_parts:
        merged.update(part)
    for _idx, _pairs in continuations.items():
        if _idx in merged:
            merged[_idx] = list(merged[_idx]) + list(_pairs)
    return merged


LONG_STORY_SETS = {
    "en": _build_story_set(
        [LONG_STORIES_A, LONG_STORIES_B, LONG_STORIES_C, LONG_STORIES_D, LONG_STORIES_E, LONG_STORIES_F],
        CONTINUATIONS,
    ),
    "ru": _build_story_set([RU_P1, RU_P2, RU_P3], CONTRU),
    "ar": _build_story_set([LONG_STORIES_AR], CONTINUATIONS_AR),
    "ko": _build_story_set([LONG_STORIES_KO], CONTINUATIONS_KO),
    "tr": _build_story_set([LONG_STORIES_TR], CONTINUATIONS_TR),
}

LANGUAGES = [
    {
        "code": "en",
        "name": "Ingliz tili",
        "description": "Xalqaro muloqotning asosiy tili — sayohat, ish va ta'limda eng ko'p ishlatiladi.",
        "emoji": "🇬🇧",
        "colors": ("#2b5876", "#4e4376"),
        "accent": "#ffd166",
        "landmark": "bigben",
    },
    {
        "code": "ru",
        "name": "Rus tili",
        "description": "MDH hududidagi eng keng tarqalgan til — savdo va aloqalar uchun foydali.",
        "emoji": "🇷🇺",
        "colors": ("#c33764", "#1d2671"),
        "accent": "#ff8fa3",
        "landmark": "onion",
    },
    {
        "code": "ar",
        "name": "Arab tili",
        "description": "Boy madaniyat va din tarixiga ega til — 25+ mamlakatda gaplashiladi.",
        "emoji": "🇸🇦",
        "colors": ("#b06a2c", "#5e3411"),
        "accent": "#ffe29a",
        "landmark": "mosque",
    },
    {
        "code": "ko",
        "name": "Koreys tili",
        "description": "K-pop va texnologiya vatani — zamonaviy o'rganuvchilar sevimli tili.",
        "emoji": "🇰🇷",
        "colors": ("#0072ff", "#00266b"),
        "accent": "#9ad0ff",
        "landmark": "ntower",
    },
    {
        "code": "tr",
        "name": "Turk tili",
        "description": "Qardosh til — o'zlashtirish oson, turizm va biznesda qo'l keladi.",
        "emoji": "🇹🇷",
        "colors": ("#a4133c", "#5c0a23"),
        "accent": "#ffc2d1",
        "landmark": "mosque",
    },
]

TOPICS = [
    ("Kundalik suhbat", "💬"),
    ("Sayohat va aeroport", "✈️"),
    ("Restoran va kafe", "☕"),
    ("Ish va ofis", "💼"),
    ("Oila va qarindoshlar", "👨\u200d👩\u200d👧"),
    ("Xarid qilish", "🛍️"),
    ("Sport va salomatlik", "⚽"),
    ("Tabiat va ob-havo", "🌿"),
    ("Ta'lim va o'qish", "🎓"),
    ("Shahar hayoti", "🏙️"),
]

ACCENTS = {item["code"]: item["accent"] for item in LANGUAGES}

# Har bir mavzu uchun 4 ta sahna; har sahna 2 gapdan iborat.
# Kalitlar: uz (tarjima), en, ru, ar, ko, tr (original tillar).
SCENES = {
    0: [
        {
            "uz": ["Assalomu alaykum! Ishlaringiz qalay?"],
            "en": ["Hello! How are you doing today?"],
            "ru": ["Привет! Как у тебя дела сегодня?"],
            "ar": ["مرحباً! كيف حالك اليوم؟"],
            "ko": ["안녕하세요! 오늘 어떻게 지내세요?"],
            "tr": ["Merhaba! Bugün nasılsın?"],
        },
        {
            "uz": ["Yaxshi, rahmat. Bugun havo juda chiroyli."],
            "en": ["I am fine, thank you. The weather is really beautiful today."],
            "ru": ["Хорошо, спасибо. Погода сегодня очень красивая."],
            "ar": ["أنا بخير، شكراً. الطقس جميل جداً اليوم."],
            "ko": ["잘 지내요, 고마워요. 오늘 날씨가 정말 좋아요."],
            "tr": ["İyiyim, teşekkür ederim. Hava bugün gerçekten çok güzel."],
        },
        {
            "uz": ["Ismingiz nima? Meni Aziz deying.", "Men Toshkentdan kelganman."],
            "en": ["What is your name? Please call me Aziz.", "I came from Tashkent."],
            "ru": ["Как вас зовут? Называйте меня Азиз.", "Я приехал из Ташкента."],
            "ar": ["ما اسمك؟ من فضلك نادني أزيز.", "لقد جئت من طشقند."],
            "ko": ["이름이 뭐예요? 저를 아지즈라고 불러 주세요.", "저는 타슈켄트에서 왔어요."],
            "tr": ["Adınız ne? Lütfen bana Aziz deyin.", "Ben Taşkent'ten geldim."],
        },
        {
            "uz": ["Tanishganimdan xursandman!", "Sizga yaxshi kun tilayman!"],
            "en": ["Nice to meet you!", "Have a great day!"],
            "ru": ["Рад знакомству!", "Хорошего вам дня!"],
            "ar": ["سررت بلقائك!", "أتمنى لك يوماً سعيداً!"],
            "ko": ["만나서 반가워요!", "좋은 하루 보내세요!"],
            "tr": ["Tanıştığımıza sevindim!", "İyi günler dilerim!"],
        },
    ],
    1: [
        {
            "uz": ["Samolyot biletimni tekshirib bera olasizmi?"],
            "en": ["Could you check my plane ticket, please?"],
            "ru": ["Вы могли бы проверить мой авиабилет?"],
            "ar": ["هل يمكنك التحقق من تذكرة الطيران من فضلك؟"],
            "ko": ["제 비행기 표를 확인해 주시겠어요?"],
            "tr": ["Uçak biletimi kontrol edebilir misiniz?"],
        },
        {
            "uz": ["Albatta, o'rningiz 12A, chiqish darvozasi esa beshinchi."],
            "en": ["Of course. Your seat is 12A and your boarding gate is number five."],
            "ru": ["Конечно. Ваше место 12A, выход на посадку номер пять."],
            "ar": ["بالتأكيد. مقعدك 12A وبوابة الصعود رقم خمسة."],
            "ko": ["물론이죠. 좌석은 12A이고 탑승구는 5번입니다."],
            "tr": ["Elbette. Koltuğunuz 12A ve biniş kapınız beş numara."],
        },
        {
            "uz": ["Aeroportdan mehmonxonaga qanday boraman?", "Taksi bilan taxminan yigirma daqiqa ketadi."],
            "en": ["How do I get to the hotel from the airport?", "It takes about twenty minutes by taxi."],
            "ru": ["Как мне добраться до отеля из аэропорта?", "На такси это займёт около двадцати минут."],
            "ar": ["كيف أصل إلى الفندق من المطار؟", "يستغرق الأمر حوالي عشرين دقيقة بالسيارة الأجرة."],
            "ko": ["공항에서 호텔까지 어떻게 가요?", "택시로 약 이십 분 정도 걸려요."],
            "tr": ["Havalimanından otel nasıl gidilir?", "Taksiyle yaklaşık yirmi dakika sürüyor."],
        },
        {
            "uz": ["Xo'sh, keyingi parvoz qachon?", "Ertalab soat to'qqizda uchamiz."],
            "en": ["So, when is the next flight?", "We fly at nine in the morning."],
            "ru": ["Итак, когда следующий рейс?", "Мы вылетаем в девять утра."],
            "ar": ["إذن، متى الرحلة التالية؟", "نطير في التاسعة صباحاً."],
            "ko": ["그럼 다음 비행기는 언제예요?", "우리는 아홉 시에 출발해요."],
            "tr": ["Peki, bir sonraki uçak ne zaman?", "Sabah dokuzda uçuyoruz."],
        },
    ],
    2: [
        {
            "uz": ["Kechki ovqat uchun stol band qilmoqchiman."],
            "en": ["I would like to reserve a table for dinner."],
            "ru": ["Я хотел бы заказать столик на ужин."],
            "ar": ["أود حجز طاولة للعشاء."],
            "ko": ["저녁 식사를 위해 테이블을 예약하고 싶어요."],
            "tr": ["Akşam yemeği için masa ayırtmak istiyorum."],
        },
        {
            "uz": ["Ikki kishi uchun soat yettida bo'ladimi?"],
            "en": ["Is seven o'clock available for two people?"],
            "ru": ["На семь часов для двоих свободно?"],
            "ar": ["هل الساعة السابعة متاحة لشخصين؟"],
            "ko": ["두 명이서 일곱 시에 가능할까요?"],
            "tr": ["Saat yedide iki kişilik mümkün mü?"],
        },
        {
            "uz": ["Menyuni ko'rsatasizmi?", "Milliy taomlaringiz qaysilar?"],
            "en": ["Could you show me the menu?", "What are your national dishes?"],
            "ru": ["Покажите меню, пожалуйста.", "Какие у вас национальные блюда?"],
            "ar": ["هل يمكنك أن تريني قائمة الطعام؟", "ما هي أطباقكم الوطنية؟"],
            "ko": ["메뉴판을 보여주시겠어요?", "어떤 현지 요리가 있어요?"],
            "tr": ["Menüyü gösterebilir misiniz?", "Yerel yemekleriniz neler?"],
        },
        {
            "uz": ["Hisobni olib keling, iltimos.", "Ovqat juda mazali bo'ldi!"],
            "en": ["Could you bring the bill, please?", "The food was very delicious!"],
            "ru": ["Принесите счёт, пожалуйста.", "Еда была очень вкусной!"],
            "ar": ["هل يمكنك إحضار الفاتورة من فضلك؟", "كان الطعام لذيذاً جداً!"],
            "ko": ["계산서를 가져다주시겠어요?", "음식이 정말 맛있었어요!"],
            "tr": ["Hesabı getirebilir misiniz, lütfen?", "Yemek çok lezzetliydi!"],
        },
    ],
    3: [
        {
            "uz": ["Bugun soat o'nda muhim uchrashuvimiz bor."],
            "en": ["We have an important meeting at ten o'clock today."],
            "ru": ["Сегодня в десять часов у нас важная встреча."],
            "ar": ["لدينا اجتماع مهم اليوم في الساعة العاشرة."],
            "ko": ["오늘 열 시에 중요한 회의가 있어요."],
            "tr": ["Bugün saat onda önemli bir toplantımız var."],
        },
        {
            "uz": ["Hisobotni ertaga erta tong tayyorlab bo'laman."],
            "en": ["I will finish the report early tomorrow morning."],
            "ru": ["Я закончу отчёт завтра рано утром."],
            "ar": ["سأنهي التقرير غداً في الصباح الباكر."],
            "ko": ["내일 아침 일찍 보고서를 끝낼 거예요."],
            "tr": ["Raporu yarın sabah erken bitireceğim."],
        },
        {
            "uz": ["Mijoz kechqurun javob xati yubordi."],
            "en": ["The client sent us a reply email in the evening."],
            "ru": ["Клиент вечером прислал нам ответное письмо."],
            "ar": ["أرسل لنا العميل رسالة رد في المساء."],
            "ko": ["고객이 저녁에 답장 이메일을 보냈어요."],
            "tr": ["Müşteri akşam bize yanıt e-postası gönderdi."],
        },
        {
            "uz": ["Loyihani muddatidan oldin tugatdik.", "Jamoa juda yaxshi ishladi."],
            "en": ["We finished the project ahead of schedule.", "The team worked very well."],
            "ru": ["Мы закончили проект раньше срока.", "Команда очень хорошо поработала."],
            "ar": ["أنهينا المشروع قبل الموعد المحدد.", "عمل الفريق بشكل جيد جداً."],
            "ko": ["프로젝트를 예정보다 일찍 끝냈어요.", "팀이 정말 잘했어요."],
            "tr": ["Projeyi planlanandan önce bitirdik.", "Ekip çok iyi çalıştı."],
        },
    ],
    4: [
        {
            "uz": ["Bizning oilamiz besh kishidan iborat."],
            "en": ["Our family consists of five people."],
            "ru": ["Наша семья состоит из пяти человек."],
            "ar": ["تتكون عائلتي من خمسة أشخاص."],
            "ko": ["우리 가족은 다섯 명이에요."],
            "tr": ["Ailemiz beş kişiden oluşuyor."],
        },
        {
            "uz": ["Otam shifokor, onam esa o'qituvchi bo'lib ishlaydi."],
            "en": ["My father is a doctor and my mother works as a teacher."],
            "ru": ["Мой отец врач, а мама работает учителем."],
            "ar": ["أبي طبيب وأمي تعمل مدرسةً."],
            "ko": ["아버지는 의사이고 어머니는 선생님으로 일하세요."],
            "tr": ["Babam doktor, annem ise öğretmen olarak çalışıyor."],
        },
        {
            "uz": ["Dam olish kunlari bobo va momolarimizga boramiz."],
            "en": ["On weekends we visit our grandparents."],
            "ru": ["По выходным мы навещаем наших дедушку и бабушку."],
            "ar": ["في عطلة نهاية الأسبوع نزور جدّنا وجدّتنا."],
            "ko": ["주말에는 조부모님을 찾아뵈러 가요."],
            "tr": ["Hafta sonlarında büyükanne ve büyükbabamızı ziyaret ederiz."],
        },
        {
            "uz": ["Singlim ingliz tilini juda yaxshi o'rganadi."],
            "en": ["My younger sister learns English very well."],
            "ru": ["Моя младшая сестра очень хорошо учит английский."],
            "ar": ["أختي الصغرى تتعلم الإنجليزية بشكل جيد جداً."],
            "ko": ["여동생은 영어를 정말 잘 배워요."],
            "tr": ["Kız kardeşim İngilizceyi çok iyi öğreniyor."],
        },
    ],
    5: [
        {
            "uz": ["Men yangi kurtka izlayapman."],
            "en": ["I am looking for a new jacket."],
            "ru": ["Я ищу новую куртку."],
            "ar": ["أبحث عن سترة جديدة."],
            "ko": ["새 재킷을 찾고 있어요."],
            "tr": ["Yeni bir ceket arıyorum."],
        },
        {
            "uz": ["Bu kurtka qancha turadi?"],
            "en": ["How much does this jacket cost?"],
            "ru": ["Сколько стоит эта куртка?"],
            "ar": ["كم ثمن هذه السترة؟"],
            "ko": ["이 재킷은 얼마예요?"],
            "tr": ["Bu ceket kaç para?"],
        },
        {
            "uz": ["Chegirma bo'lsa, ikkita olaman."],
            "en": ["If there is a discount, I will buy two."],
            "ru": ["Если будет скидка, я куплю две."],
            "ar": ["إذا كان هناك خصم، سأشتري اثنتين."],
            "ko": ["할인이 있다면 두 개 살 거예요."],
            "tr": ["İndirim varsa iki tane alırım."],
        },
        {
            "uz": ["Karta bilan to'lasa ham bo'ladimi?"],
            "en": ["Can I also pay by card?"],
            "ru": ["Можно также оплатить картой?"],
            "ar": ["هل يمكنني الدفع بالبطاقة أيضاً؟"],
            "ko": ["카드로도 계산할 수 있나요?"],
            "tr": ["Kartla da ödeyebilir miyim?"],
        },
    ],
    6: [
        {
            "uz": ["Har kuni ertalab yigirma daqiqa yuguraman."],
            "en": ["Every morning I run for twenty minutes."],
            "ru": ["Каждое утро я бегаю двадцать минут."],
            "ar": ["كل صباح أجري لمدة عشرين دقيقة."],
            "ko": ["매일 아침 이십 분간 달려요."],
            "tr": ["Her sabah yirmi dakika koşuyorum."],
        },
        {
            "uz": ["Shanba kunlari do'stlarim bilan futbol o'ynaymiz."],
            "en": ["On Saturdays I play football with my friends."],
            "ru": ["По субботам я играю в футбол с друзьями."],
            "ar": ["أيام السبت ألعب كرة القدم مع أصدقائي."],
            "ko": ["토요일에는 친구들과 축구를 해요."],
            "tr": ["Cumartesileri arkadaşlarımla futbol oynuyorum."],
        },
        {
            "uz": ["Sport bilan birga sog'lom ovqatlanish ham muhim."],
            "en": ["Along with sports, healthy eating is also important."],
            "ru": ["Вместе со спортом важно и здоровое питание."],
            "ar": ["مع الرياضة، فإن الأكل الصحي مهم أيضاً."],
            "ko": ["운동과 함께 건강한 식사도 중요해요."],
            "tr": ["Sporla birlikte sağlıklı beslenme de önemli."],
        },
        {
            "uz": ["Maqsadim uch oyda yarim marafonga tayyorlanish."],
            "en": ["My goal is to prepare for a half marathon in three months."],
            "ru": ["Моя цель — подготовиться к полумарафону за три месяца."],
            "ar": ["هدفي أن أستعد لنصف الماراثون خلال ثلاثة أشهر."],
            "ko": ["제 목표는 석 달 안에 하프 마라톤을 준비하는 거예요."],
            "tr": ["Hedefim üç ayda yarım maratona hazırlanmak."],
        },
    ],
    7: [
        {
            "uz": ["Bugun quyoshli, lekin shamol sal kuchli."],
            "en": ["Today it is sunny, but the wind is a bit strong."],
            "ru": ["Сегодня солнечно, но ветер немного сильный."],
            "ar": ["الجو مشمس اليوم لكن الريح قوية قليلاً."],
            "ko": ["오늘은 화창하지만 바람이 조금 강해요."],
            "tr": ["Bugün güneşli ama rüzgar biraz güçlü."],
        },
        {
            "uz": ["Bahorda tog'larga chiqishni yoqtiraman."],
            "en": ["In spring I like going to the mountains."],
            "ru": ["Весной я люблю ходить в горы."],
            "ar": ["في الربيع أحب الذهاب إلى الجبال."],
            "ko": ["봄에는 산에 가는 것을 좋아해요."],
            "tr": ["İlkbaharda dağlara gitmeyi severim."],
        },
        {
            "uz": ["Ertaga yomg'ir yog'ishi kutilmoqda, soyabon oling."],
            "en": ["Rain is expected tomorrow, take an umbrella."],
            "ru": ["Завтра ожидается дождь, возьмите зонт."],
            "ar": ["من المتوقع أن تمطر غداً، خذ معك مظلة."],
            "ko": ["내일 비가 올 예정이에요, 우산 챙기세요."],
            "tr": ["Yarın yağmur bekleniyor, şemsiye alın."],
        },
        {
            "uz": ["Dengiz bo'yida quyosh botishini tomosha qilish yoqadi."],
            "en": ["I enjoy watching the sunset by the sea."],
            "ru": ["Мне нравится наблюдать закат у моря."],
            "ar": ["أستمتع بمشاهدة غروب الشمس عند البحر."],
            "ko": ["바닷가에서 노을을 보는 것을 즐겨요."],
            "tr": ["Deniz kenarında gün batımını izlemekten hoşlanırım."],
        },
    ],
    8: [
        {
            "uz": ["Har kuni yarim soat yangi so'z yodlayman."],
            "en": ["Every day I memorize new words for half an hour."],
            "ru": ["Каждый день я полчаса учу новые слова."],
            "ar": ["كل يوم أحفظ كلمات جديدة لنصف ساعة."],
            "ko": ["매일 반 시간 동안 새 단어를 외워요."],
            "tr": ["Her gün yarım saat yeni kelime ezberliyorum."],
        },
        {
            "uz": ["Ko'p kitob o'qish tilni tez o'rgatadi."],
            "en": ["Reading many books helps you learn a language quickly."],
            "ru": ["Чтение многих книг помогает быстро выучить язык."],
            "ar": ["قراءة الكتب الكثير يساعد على تعلم اللغة بسرعة."],
            "ko": ["책을 많이 읽으면 언어를 빨리 배우는 데 도움이 돼요."],
            "tr": ["Çok kitap okumak dili hızlı öğrenmeye yardımcı olur."],
        },
        {
            "uz": ["Darsdan keyin o'qituvchimga savol berdim."],
            "en": ["After the lesson I asked my teacher a question."],
            "ru": ["После урока я задал вопрос своему учителю."],
            "ar": ["بعد الدرس سألت معلمي سؤالاً."],
            "ko": ["수업 후에 선생님께 질문을 했어요."],
            "tr": ["Dersten sonra öğretmenime bir soru sordum."],
        },
        {
            "uz": ["Yozda xalqaro imtihonga topshiraman."],
            "en": ["In summer I will take an international exam."],
            "ru": ["Летом я сдам международный экзамен."],
            "ar": ["في الصيف سأخضع لامتحان دولي."],
            "ko": ["여름에 국제 시험을 볼 거예요."],
            "tr": ["Yazın uluslararası bir sınava gireceğim."],
        },
    ],
    9: [
        {
            "uz": ["Metro bilan ishga tez yetib boraman."],
            "en": ["I get to work quickly by metro."],
            "ru": ["На метро я быстро добираюсь до работы."],
            "ar": ["أصل إلى العمل بسرعة بالمتريو."],
            "ko": ["지하철로 빨리 출근해요."],
            "tr": ["Metroyla işe hızlıca gidiyorum."],
        },
        {
            "uz": ["Shahar markazida yangi kutubxona ochildi."],
            "en": ["A new library has opened in the city center."],
            "ru": ["В центре города открылась новая библиотека."],
            "ar": ["افتتحت مكتبة جديدة في وسط المدينة."],
            "ko": ["시내 중심가에 새 도서관이 문을 열었어요."],
            "tr": ["Şehir merkezinde yeni bir kütüphane açıldı."],
        },
        {
            "uz": ["Kechqurun parkda sayr qilishni yaxshi ko'raman."],
            "en": ["In the evening I like walking in the park."],
            "ru": ["Вечером я люблю гулять в парке."],
            "ar": ["في المساء أحب التنزه في الحديقة."],
            "ko": ["저녁에는 공원에서 산책하는 것을 좋아해요."],
            "tr": ["Akşamları parkta yürümeyi severim."],
        },
        {
            "uz": ["Katta shaharda hayot juda shoshqaloq, lekin qiziq."],
            "en": ["Life in a big city is very busy but interesting."],
            "ru": ["Жизнь в большом городе очень суетливая, но интересная."],
            "ar": ["الحياة في المدينة الكبيرة مزدحمة جداً لكنها مثيرة للاهتمام."],
            "ko": ["큰 도시의 삶은 아주 바쁘지만 재미있어요."],
            "tr": ["Büyük şehirdeki hayat çok yoğun ama ilginç."],
        },
    ],
}

FEATURED_TOPICS = {0, 1}


def _landmark(kind, accent):
    """Shahar silueti — qorong'u bino shakllari, pastdagi chiziq y=470."""
    dark = "#0c0a18"
    if kind == "bigben":
        return f"""
  <g opacity="0.92">
    <rect x="60" y="380" width="90" height="90" fill="{dark}"/>
    <rect x="140" y="250" width="54" height="220" fill="{dark}"/>
    <polygon points="136,250 198,250 167,198" fill="{dark}"/>
    <circle cx="167" cy="288" r="15" fill="{accent}"/>
    <line x1="167" y1="288" x2="167" y2="278" stroke="{dark}" stroke-width="2.5"/>
    <line x1="167" y1="288" x2="175" y2="292" stroke="{dark}" stroke-width="2.5"/>
    <rect x="194" y="345" width="130" height="125" fill="{dark}"/>
    <rect x="330" y="400" width="80" height="70" fill="{dark}"/>
  </g>"""
    if kind == "onion":
        return f"""
  <g opacity="0.92">
    <rect x="95" y="365" width="60" height="105" fill="{dark}"/>
    <rect x="150" y="330" width="74" height="140" fill="{dark}"/>
    <path d="M 150 332 Q 187 226 224 332 Z" fill="{dark}"/>
    <rect x="184" y="196" width="6" height="36" fill="{dark}"/>
    <polygon points="187,186 195,200 187,214 179,200" fill="{accent}"/>
    <rect x="224" y="395" width="110" height="75" fill="{dark}"/>
    <path d="M 268 396 Q 279 356 290 396 Z" fill="{dark}"/>
  </g>"""
    if kind == "mosque":
        return f"""
  <g opacity="0.92">
    <rect x="118" y="340" width="116" height="130" fill="{dark}"/>
    <path d="M 112 342 A 64 64 0 0 1 240 342 Z" fill="{dark}"/>
    <rect x="176" y="236" width="6" height="46" fill="{dark}"/>
    <circle cx="179" cy="232" r="7" fill="{accent}"/>
    <rect x="62" y="255" width="17" height="215" fill="{dark}"/>
    <polygon points="61,255 79,255 70,228" fill="{dark}"/>
    <circle cx="70" cy="222" r="5" fill="{accent}"/>
    <rect x="272" y="255" width="17" height="215" fill="{dark}"/>
    <polygon points="271,255 289,255 280,228" fill="{dark}"/>
    <circle cx="280" cy="222" r="5" fill="{accent}"/>
  </g>"""
    if kind == "ntower":
        return f"""
  <g opacity="0.92">
    <rect x="158" y="292" width="20" height="178" fill="{dark}"/>
    <ellipse cx="168" cy="278" rx="40" ry="24" fill="{dark}"/>
    <ellipse cx="168" cy="278" rx="24" ry="13" fill="{accent}" opacity="0.85"/>
    <rect x="165" y="212" width="6" height="44" fill="{dark}"/>
    <rect x="60" y="400" width="80" height="70" fill="{dark}"/>
    <rect x="220" y="370" width="66" height="100" fill="{dark}"/>
    <rect x="292" y="412" width="90" height="58" fill="{dark}"/>
  </g>"""
    return ""


def _stars():
    pts = [
        (90, 70), (160, 130), (240, 60), (330, 110), (420, 55), (520, 95),
        (600, 50), (700, 120), (750, 65), (120, 190), (480, 160), (650, 170),
    ]
    return "".join(
        f'<circle cx="{x}" cy="{y}" r="{2 if i % 3 else 3}" fill="#ffffff" opacity="{0.25 + (i % 4) * 0.12}"/>'
        for i, (x, y) in enumerate(pts)
    )


def _skyline_filler(accent):
    blocks = [
        (430, 60, 70), (500, 46, 108), (556, 70, 84), (636, 52, 126),
        (698, 72, 92), (300, 56, 96),
    ]
    parts = ['<g opacity="0.8">']
    for i, (x, w, h) in enumerate(blocks):
        parts.append(f'<rect x="{x}" y="{470 - h}" width="{w}" height="{h}" fill="#0c0a18"/>')
        for wx in range(x + 10, x + w - 8, 16):
            for wy in range(470 - h + 12, 462, 22):
                if (wx + wy + i) % 3 == 0:
                    parts.append(
                        f'<rect x="{wx}" y="{wy}" width="6" height="9" fill="{accent}" opacity="0.55"/>'
                    )
    parts.append("</g>")
    return "\n".join(parts)


SKIES = [
    {"c1": "#42275a", "c2": "#734b6d", "sun": (165, 315, 42, "#ffd9a0"), "stars": False},
    {"c1": "#0f4c81", "c2": "#4aa3df", "sun": (480, 105, 36, "#fff6d8"), "stars": False},
    {"c1": "#c33764", "c2": "#f2994a", "sun": (545, 195, 54, "#ffb347"), "stars": False},
    {"c1": "#0d1033", "c2": "#33357a", "sun": (640, 105, 32, "#ffffff"), "stars": True},
]
SKY_OFFSET = {"en": 1, "ru": 2, "ar": 0, "ko": 3, "tr": 2}


def _city_stars(night):
    pts = [
        (70, 55), (150, 120), (235, 65), (320, 115), (410, 50), (505, 95),
        (585, 45), (690, 125), (755, 60), (110, 175), (455, 155), (720, 185),
        (280, 150), (620, 90),
    ]
    out = ""
    if night:
        for i, (x, y) in enumerate(pts):
            out += f'<circle cx="{x}" cy="{y}" r="{2 if i % 3 else 3}" fill="#ffffff" opacity="{0.3 + (i % 4) * 0.15}"/>'
    else:
        for i, (x, y) in enumerate(pts[:5]):
            out += f'<circle cx="{x}" cy="{y}" r="2" fill="#ffffff" opacity="0.18"/>'
    return out


def _windows(x0, y0, w, h, accent):
    parts = []
    for wx in range(x0 + 8, x0 + w - 8, 15):
        for wy in range(y0 + 10, y0 + h - 8, 20):
            if (wx * 7 + wy * 13) % 4 == 0:
                parts.append(f'<rect x="{wx}" y="{wy}" width="6" height="9" fill="{accent}" opacity="0.6"/>')
    return "".join(parts)


def _city_landmark(code, accent):
    d = "#0d0b1e"
    if code == "en":
        return f"""
  <g>
    <rect x="118" y="212" width="52" height="218" fill="{d}"/>
    <polygon points="114,212 174,212 144,158" fill="{d}"/>
    <circle cx="144" cy="250" r="14" fill="{accent}"/>
    <line x1="144" y1="250" x2="144" y2="240" stroke="{d}" stroke-width="2.5"/>
    <line x1="144" y1="250" x2="152" y2="255" stroke="{d}" stroke-width="2.5"/>
    <rect x="170" y="332" width="152" height="98" fill="{d}"/>
    {"".join(f'<rect x="{186 + i*22}" y="320" width="8" height="14" fill="{d}"/>' for i in range(7))}
    {_windows(178, 344, 136, 78, accent)}
    <rect x="424" y="252" width="40" height="178" fill="{d}"/>
    <polygon points="420,252 468,252 444,216" fill="{d}"/>
    <rect x="566" y="252" width="40" height="178" fill="{d}"/>
    <polygon points="562,252 610,252 586,216" fill="{d}"/>
    <rect x="384" y="362" width="246" height="14" fill="{d}"/>
    <path d="M 384 358 C 430 306 470 306 566 322 M 606 358 C 650 330 700 342 736 352" stroke="{d}" stroke-width="6" fill="none"/>
  </g>"""
    if code == "ru":
        return f"""
  <g>
    <rect x="200" y="382" width="400" height="48" fill="{d}"/>
    {"".join(f'<rect x="{204 + i*24}" y="370" width="14" height="14" fill="{d}"/>' for i in range(17))}
    <rect x="286" y="330" width="38" height="100" fill="{d}"/>
    <path d="M 286 332 Q 305 264 324 332 Z" fill="#c0392b"/>
    <rect x="303" y="238" width="4" height="26" fill="#ffd166"/>
    <rect x="356" y="256" width="46" height="174" fill="{d}"/>
    <polygon points="352,256 406,256 379,192" fill="{d}"/>
    <circle cx="379" cy="228" r="5" fill="#ffd166"/>
    <rect x="442" y="316" width="42" height="114" fill="{d}"/>
    <path d="M 442 318 Q 463 244 484 318 Z" fill="#f1c40f"/>
    <rect x="462" y="216" width="4" height="30" fill="#ffd166"/>
    <rect x="516" y="348" width="34" height="82" fill="{d}"/>
    <path d="M 516 350 Q 533 292 550 350 Z" fill="#2980b9"/>
  </g>"""
    if code == "ar":
        return f"""
  <g>
    <rect x="396" y="108" width="5" height="44" fill="{d}"/>
    <polygon points="392,150 405,150 414,430 383,430" fill="{d}"/>
    <rect x="380" y="252" width="37" height="178" fill="{d}"/>
    <rect x="370" y="316" width="57" height="114" fill="{d}"/>
    <rect x="358" y="368" width="81" height="62" fill="{d}"/>
    {_windows(366, 378, 64, 44, accent)}
    <rect x="470" y="270" width="34" height="160" fill="{d}"/>
    <rect x="464" y="300" width="46" height="130" fill="{d}"/>
    <rect x="540" y="330" width="28" height="100" fill="{d}"/>
    <rect x="250" y="310" width="40" height="120" fill="{d}"/>
    <rect x="242" y="342" width="56" height="88" fill="{d}"/>
    <ellipse cx="270" cy="312" rx="24" ry="10" fill="{accent}" opacity="0.5"/>
  </g>"""
    if code == "ko":
        return f"""
  <g>
    <path d="M 70 430 Q 220 352 380 430 Z" fill="{d}"/>
    <rect x="208" y="272" width="16" height="92" fill="{d}"/>
    <ellipse cx="216" cy="264" rx="36" ry="21" fill="{d}"/>
    <ellipse cx="216" cy="264" rx="22" ry="12" fill="{accent}" opacity="0.85"/>
    <rect x="213" y="218" width="6" height="42" fill="{d}"/>
    <circle cx="216" cy="214" r="4" fill="#ff5f8f"/>
    <rect x="430" y="290" width="52" height="140" fill="{d}"/>
    {_windows(434, 300, 44, 122, accent)}
    <rect x="496" y="330" width="40" height="100" fill="{d}"/>
    {_windows(500, 340, 32, 82, accent)}
    <rect x="556" y="262" width="58" height="168" fill="{d}"/>
    {_windows(562, 274, 46, 148, accent)}
    <rect x="636" y="322" width="36" height="108" fill="{d}"/>
    {_windows(640, 332, 28, 90, accent)}
    <path d="M 420 430 Q 560 396 720 424" stroke="{d}" stroke-width="7" fill="none"/>
  </g>"""
    if code == "tr":
        return f"""
  <g>
    <rect x="216" y="342" width="128" height="88" fill="{d}"/>
    <path d="M 208 344 A 72 72 0 0 1 352 344 Z" fill="{d}"/>
    <rect x="276" y="240" width="6" height="42" fill="{d}"/>
    <circle cx="279" cy="234" r="7" fill="{accent}"/>
    <rect x="188" y="228" width="16" height="202" fill="{d}"/>
    <polygon points="186,228 206,228 196,204" fill="{d}"/>
    <circle cx="196" cy="198" r="5" fill="{accent}"/>
    <rect x="358" y="228" width="16" height="202" fill="{d}"/>
    <polygon points="356,228 376,228 366,204" fill="{d}"/>
    <circle cx="366" cy="198" r="5" fill="{accent}"/>
    <rect x="552" y="286" width="56" height="144" fill="{d}"/>
    <rect x="548" y="304" width="64" height="10" fill="{accent}" opacity="0.7"/>
    <polygon points="546,286 614,286 580,238" fill="{d}"/>
    <path d="M 640 430 Q 700 402 762 418" stroke="{d}" stroke-width="6" fill="none"/>
  </g>"""
    return ""


def _water(accent):
    lines = [
        (90, 452, 60), (200, 466, 84), (330, 455, 50), (430, 470, 96),
        (560, 452, 70), (660, 468, 88), (730, 455, 46), (150, 484, 70),
        (390, 488, 60), (600, 486, 74),
    ]
    parts = ['<rect x="0" y="440" width="800" height="60" fill="#070d1f" opacity="0.92"/>']
    for i, (x, y, w) in enumerate(lines):
        col = accent if i % 3 == 0 else "#ffffff"
        op = 0.28 if i % 3 == 0 else 0.16
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="{col}" opacity="{op}"/>')
    return "\n  ".join(parts)


def write_city_cover(filename, code, title, emoji, variant_idx):
    """Kitob muqovasi — til davlatining mashhur shahri manzarasi."""
    covers_dir = os.path.join(settings.MEDIA_ROOT, "covers")
    os.makedirs(covers_dir, exist_ok=True)
    sky = SKIES[variant_idx % len(SKIES)]
    c1, c2 = sky["c1"], sky["c2"]
    sx, sy, sr, scol = sky["sun"]
    accent = ACCENTS[code]
    title_escaped = title.replace("&", "&amp;").replace("<", "&lt;")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.55"/>
    </linearGradient>
  </defs>
  <rect width="800" height="500" rx="28" fill="url(#sky)"/>
  {_city_stars(sky["stars"])}
  <circle cx="{sx}" cy="{sy}" r="{sr * 2}" fill="{scol}" opacity="0.12"/>
  <circle cx="{sx}" cy="{sy}" r="{sr}" fill="{scol}" opacity="0.85"/>
  {_city_landmark(code, accent)}
  {_water(accent)}
  <rect width="800" height="500" rx="28" fill="url(#fade)"/>
  <text x="36" y="58" font-family="Segoe UI, Roboto, Arial" font-size="22" fill="#ffffff" opacity="0.8" letter-spacing="5">LINGUO</text>
  <g transform="translate(648,180)">
    <circle cx="52" cy="52" r="52" fill="#ffffff" opacity="0.16"/>
    <text x="52" y="97" font-size="120" text-anchor="middle">{emoji}</text>
  </g>
  <text x="36" y="432" font-family="Segoe UI, Roboto, Arial" font-size="42" font-weight="bold" fill="#ffffff">{title_escaped}</text>
</svg>
"""
    path = os.path.join(covers_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return f"covers/{filename}"


def write_svg_cover(filename, title, emoji, c1, c2, accent="#ffd166", landmark="", subtitle="LINGUO"):
    covers_dir = os.path.join(settings.MEDIA_ROOT, "covers")
    os.makedirs(covers_dir, exist_ok=True)
    title_escaped = title.replace("&", "&amp;").replace("<", "&lt;")
    emoji_size = 120 if landmark else 150
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#000000" stop-opacity="0"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.55"/>
    </linearGradient>
  </defs>
  <rect width="800" height="500" rx="28" fill="url(#sky)"/>
  {_stars()}
  <circle cx="655" cy="115" r="70" fill="#ffffff" opacity="0.14"/>
  <circle cx="655" cy="115" r="38" fill="#ffffff" opacity="0.30"/>
  <rect x="0" y="440" width="800" height="60" fill="#0c0a18"/>
  {_landmark(landmark, accent)}
  {_skyline_filler(accent)}
  <rect width="800" height="500" rx="28" fill="url(#fade)"/>
  <text x="36" y="58" font-family="Segoe UI, Roboto, Arial" font-size="22" fill="#ffffff" opacity="0.8" letter-spacing="5">{subtitle}</text>
  <g transform="translate(648,180)">
    <circle cx="52" cy="52" r="52" fill="#ffffff" opacity="0.16"/>
    <text x="52" y="{52 + emoji_size * 0.36}" font-size="{emoji_size}" text-anchor="middle">{emoji}</text>
  </g>
  <text x="36" y="432" font-family="Segoe UI, Roboto, Arial" font-size="42" font-weight="bold" fill="#ffffff">{title_escaped}</text>
</svg>
"""
    path = os.path.join(covers_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return f"covers/{filename}"


class Command(BaseCommand):
    help = "LINGUO kontentini seed qiladi: tillar, kitoblar, bo'limlar, coverlar, yutuqlar"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Avval kontent jadvallarini tozalash")

    def handle(self, *args, **options):
        if options["reset"]:
            BookSection.objects.all().delete()
            Book.objects.all().delete()
            Language.objects.all().delete()
            self.stdout.write("Eski kontent o'chirildi.")

        for i, (code, title, icon, desc) in enumerate(ACHIEVEMENT_SEED):
            Achievement.objects.update_or_create(
                code=code,
                defaults={"title": title, "icon": icon, "condition_description": desc},
            )
        self.stdout.write(f"{len(ACHIEVEMENT_SEED)} ta yutuq seed qilindi.")

        sections_total = 0
        for lang_index, lang_data in enumerate(LANGUAGES):
            photo_rel = f"covers/photos/lang_{lang_data['code']}.jpg"
            photo_abs = os.path.join(settings.MEDIA_ROOT, *photo_rel.split("/"))
            if os.path.exists(photo_abs):
                cover_path = photo_rel
            else:
                cover_path = write_city_cover(
                    f"lang_{lang_data['code']}_v2.svg",
                    lang_data["code"],
                    lang_data["name"],
                    lang_data["emoji"],
                    SKY_OFFSET[lang_data["code"]],
                )
            language, _ = Language.objects.update_or_create(
                code=lang_data["code"],
                defaults={
                    "name": lang_data["name"],
                    "description": lang_data["description"],
                    "cover_image_url": cover_path,
                    "order_index": lang_index,
                    "is_featured": lang_data["code"] in ("en", "ru"),
                },
            )

            for topic_index, (topic, topic_emoji) in enumerate(TOPICS):
                book_cover = write_city_cover(
                    f"book_{lang_data['code']}_{topic_index}_v2.svg",
                    lang_data["code"],
                    topic,
                    topic_emoji,
                    topic_index + SKY_OFFSET[lang_data["code"]],
                )
                book, _ = Book.objects.update_or_create(
                    language=language,
                    order_index=topic_index,
                    defaults={
                        "topic": topic,
                        "emoji": topic_emoji,
                        "cover_image_url": book_cover,
                        "is_featured": topic_index in FEATURED_TOPICS,
                    },
                )

                lang_stories = LONG_STORY_SETS.get(lang_data["code"], {})
                if topic_index in lang_stories:
                    pairs = lang_stories[topic_index]
                    section_data = [([p[0] for p in pairs], [p[1] for p in pairs])]
                else:
                    section_data = [
                        (scene[lang_data["code"]], scene["uz"]) for scene in SCENES[topic_index]
                    ]

                new_sections = [
                    (" ".join(orig), " ".join(uz)) for orig, uz in section_data
                ]
                existing = {s.order_index: s for s in book.sections.all()}
                identical = (
                    sorted(existing.keys()) == list(range(len(new_sections)))
                    and all(
                        existing[i].original_text == txt and existing[i].translated_text == trn
                        for i, (txt, trn) in enumerate(new_sections)
                    )
                )
                if identical:
                    continue

                BookSection.objects.filter(book=book).delete()
                for section_index, (original_sentences, uz_sentences) in enumerate(section_data):
                    BookSection.objects.create(
                        book=book,
                        order_index=section_index,
                        original_text=" ".join(original_sentences),
                        translated_text=" ".join(uz_sentences),
                        sentences=list(original_sentences),
                        translated_sentences=list(uz_sentences),
                    )
                    sections_total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Tayyor: {Language.objects.count()} til, {Book.objects.count()} kitob, "
                f"{sections_total} bo'lim."
            )
        )
