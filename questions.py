WELCOME_MESSAGE = (
    "🐾 <b>به Petinex خوش آمدید!</b>\n\n"
    "سلام! من قراره یه چکاپ هوشمند از وضعیت سلامت رفیق پشمالوت انجام بدم.\n\n"
    "📋 <b>این ارزیابی شامل چیه؟</b>\n"
    "• ۲۰ سؤال کوتاه و دقیق\n"
    "• حدود ۵ دقیقه زمان\n"
    "• یک گزارش شخصی‌سازی‌شده علمی\n\n"
    "⚠️ <b>نکته مهم:</b> این ارزیابی جایگزین معاینه دامپزشک نیست، "
    "اما بهت کمک می‌کنه وضعیت کلی رو بهتر بشناسی.\n\n"
    "آماده‌ای شروع کنیم؟ 👇"
)

START_BUTTON_TEXT = "🚀 شروع ارزیابی"

TRANSITIONS = {
    "section_1": "📌 <b>بخش ۱ از ۶: پروفایل بیولوژیک</b>\nبذار اول یکم بیشتر باهاش آشنا بشم...",
    "section_2": "📌 <b>بخش ۲ از ۶: تغذیه واقعی</b>\nحالا بریم سراغ غذا خوردنش...",
    "section_3": "📌 <b>بخش ۳ از ۶: وضعیت بدنی</b>\nیه نگاه به فرم بدنش بندازیم...",
    "section_4": "📌 <b>بخش ۴ از ۶: فعالیت و سبک زندگی</b>\nببینیم چقدر تحرک داره...",
    "section_5": "📌 <b>بخش ۵ از ۶: سیگنال‌های بالینی</b>\nیه سری علائم مهم رو چک کنیم...",
    "section_6": "📌 <b>بخش ۶ از ۶: رفتار و استرس</b>\nآخرین بخش - وضعیت روحیش...",
}

COMPLETION_MESSAGE = (
    "✅ <b>ممنون که وقت گذاشتی!</b>\n\n"
    "گزارش سلامت اختصاصی رفیقت داره آماده میشه...\n"
    "🕐 تا ۲۴ ساعت آینده برات ارسال میشه.\n\n"
    "اگه سؤالی داشتی، همینجا پیام بده. 🐾"
)

QUESTIONS = [
    {
        "id": 1,
        "section": 1,
        "variable": "pet_type",
        "text": "🐕 رفیقت سگه یا گربه؟",
        "type": "inline_button",
        "options": [
            {"text": "🐕 سگ", "value": "dog"},
            {"text": "🐈 گربه", "value": "cat"},
        ],
        "micro_copy": None,
    },
    {
        "id": 2,
        "section": 1,
        "variable": "breed",
        "text": "نژادش چیه؟",
        "type": "text_input",
        "options": None,
        "micro_copy": "💡 اگه دورگه‌ست یا نمی‌دونی، بنویس «دورگه» یا «نمی‌دونم»",
    },
    {
        "id": 3,
        "section": 1,
        "variable": "age_months",
        "text": "چند ماهشه؟",
        "type": "text_input",
        "options": None,
        "micro_copy": "💡 مثلاً اگه ۲ سالشه بنویس 24، اگه ۶ ماهشه بنویس 6",
    },
    {
        "id": 4,
        "section": 1,
        "variable": "sex",
        "text": "جنسیتش چیه؟",
        "type": "inline_button",
        "options": [
            {"text": "♂️ نر", "value": "male"},
            {"text": "♀️ ماده", "value": "female"},
        ],
        "micro_copy": None,
    },
    {
        "id": 5,
        "section": 1,
        "variable": "neutered",
        "text": "عقیم شده؟",
        "type": "inline_button",
        "options": [
            {"text": "✅ بله", "value": "yes"},
            {"text": "❌ خیر", "value": "no"},
            {"text": "🤷 نمی‌دونم", "value": "unknown"},
        ],
        "micro_copy": None,
    },
    {
        "id": 6,
        "section": 2,
        "variable": "food_type",
        "text": "غذای اصلیش چیه؟",
        "type": "inline_button",
        "options": [
            {"text": "🥫 خشک (کیبل)", "value": "dry"},
            {"text": "🥘 کنسرو/پوچ", "value": "wet"},
            {"text": "🍖 خونگی/پخته", "value": "homemade"},
            {"text": "🥩 خام (BARF)", "value": "raw"},
            {"text": "🔀 ترکیبی", "value": "mixed"},
        ],
        "micro_copy": None,
    },
    {
        "id": 7,
        "section": 2,
        "variable": "meals_per_day",
        "text": "روزی چند وعده غذا می‌خوره؟",
        "type": "inline_button",
        "options": [
            {"text": "۱ وعده", "value": "1"},
            {"text": "۲ وعده", "value": "2"},
            {"text": "۳ وعده", "value": "3"},
            {"text": "۴+ وعده", "value": "4plus"},
            {"text": "🍽️ همیشه پره (Free-feeding)", "value": "free"},
        ],
        "micro_copy": None,
    },
    {
        "id": 8,
        "section": 2,
        "variable": "eating_duration_minutes",
        "text": "وقتی غذاشو میذاری، چند دقیقه طول می‌کشه کامل بخوره؟",
        "type": "inline_button",
        "options": [
            {"text": "⚡ کمتر از ۲ دقیقه", "value": "lt2"},
            {"text": "🕐 ۲ تا ۱۰ دقیقه", "value": "2to10"},
            {"text": "🕑 ۱۰ تا ۳۰ دقیقه", "value": "10to30"},
            {"text": "🐌 بیشتر از ۳۰ دقیقه یا نصفه می‌ذاره", "value": "gt30"},
        ],
        "micro_copy": "💡 این سؤال کمک می‌کنه بفهمیم اشتهاش واقعاً چطوره",
    },
    {
        "id": 9,
        "section": 2,
        "variable": "treats_per_day",
        "text": "روزانه چند تا تشویقی/تنقلات می‌خوره؟",
        "type": "inline_button",
        "options": [
            {"text": "🚫 هیچی", "value": "0"},
            {"text": "۱-۲ تا", "value": "1to2"},
            {"text": "۳-۵ تا", "value": "3to5"},
            {"text": "۶+ تا", "value": "6plus"},
        ],
        "micro_copy": "💡 شامل بیسکویت، تشویقی، تکه‌های گوشت، پنیر و...",
    },
    {
        "id": 10,
        "section": 2,
        "variable": "table_scraps",
        "text": "از غذای خودتون (سفره) بهش می‌دید؟",
        "type": "inline_button",
        "options": [
            {"text": "🚫 هرگز", "value": "never"},
            {"text": "🔸 گاهی (هفته‌ای ۱-۲ بار)", "value": "sometimes"},
            {"text": "🔶 اغلب (تقریباً هر روز)", "value": "often"},
            {"text": "🔴 همیشه (هر وعده)", "value": "always"},
        ],
        "micro_copy": None,
    },
    {
        "id": 11,
        "section": 3,
        "variable": "weight_kg",
        "text": "وزنش چند کیلوئه؟",
        "type": "text_input",
        "options": None,
        "micro_copy": "💡 اگه دقیق نمی‌دونی، تخمین بزن. مثلاً: 8.5",
    },
    {
        "id": 12,
        "section": 3,
        "variable": "ribs_feel",
        "text": "وقتی دستت رو روی پهلوهاش می‌کشی، دنده‌هاش چطوری حس میشن؟",
        "type": "inline_button",
        "options": [
            {"text": "🦴 خیلی واضح و برجسته", "value": "very_visible"},
            {"text": "✅ با فشار کم حس میشن", "value": "easily_felt"},
            {"text": "🔶 باید فشار بدم تا حسشون کنم", "value": "hard_to_feel"},
            {"text": "❌ اصلاً حس نمیشن", "value": "not_felt"},
        ],
        "micro_copy": "💡 این روش ساده‌ترین تست برای تشخیص وزن ایده‌آله",
    },
    {
        "id": 13,
        "section": 3,
        "variable": "waist_shape",
        "text": "وقتی از بالا نگاهش می‌کنی، کمرش چه شکلیه؟",
        "type": "inline_button",
        "options": [
            {"text": "⌛ گودی واضح داره", "value": "clear_waist"},
            {"text": "➖ تقریباً صاف یا کمی گود", "value": "slight_waist"},
            {"text": "🫃 بیضی/گرد - گودی نداره", "value": "no_waist"},
        ],
        "micro_copy": None,
    },
    {
        "id": 14,
        "section": 4,
        "variable": "daily_walk_minutes",
        "text": "روزانه چند دقیقه پیاده‌روی یا بازی فعال داره؟",
        "type": "inline_button",
        "options": [
            {"text": "🚫 تقریباً هیچی", "value": "0"},
            {"text": "🚶 کمتر از ۱۵ دقیقه", "value": "lt15"},
            {"text": "🏃 ۱۵ تا ۳۰ دقیقه", "value": "15to30"},
            {"text": "🏃‍♂️ ۳۰ تا ۶۰ دقیقه", "value": "30to60"},
            {"text": "🏃‍♂️💨 بیشتر از ۶۰ دقیقه", "value": "gt60"},
        ],
        "micro_copy": "💡 برای گربه‌ها: بازی با اسباب‌بازی، لیزر، پر...",
    },
    {
        "id": 15,
        "section": 4,
        "variable": "living_space",
        "text": "بیشتر وقتش رو کجا می‌گذرونه؟",
        "type": "inline_button",
        "options": [
            {"text": "🏠 داخل آپارتمان", "value": "indoor_apartment"},
            {"text": "🏡 داخل خونه ویلایی", "value": "indoor_house"},
            {"text": "🌳 دسترسی به حیاط/بالکن", "value": "with_outdoor"},
            {"text": "🌲 بیشتر بیرون", "value": "mostly_outdoor"},
        ],
        "micro_copy": None,
    },
    {
        "id": 16,
        "section": 4,
        "variable": "rest_hours",
        "text": "تخمین می‌زنی روزی چند ساعت می‌خوابه یا استراحت می‌کنه؟",
        "type": "inline_button",
        "options": [
            {"text": "😴 کمتر از ۱۰ ساعت", "value": "lt10"},
            {"text": "💤 ۱۰ تا ۱۴ ساعت", "value": "10to14"},
            {"text": "😪 ۱۴ تا ۱۸ ساعت", "value": "14to18"},
            {"text": "🛌 بیشتر از ۱۸ ساعت", "value": "gt18"},
        ],
        "micro_copy": "💡 گربه‌ها معمولاً ۱۲-۱۶ ساعت، سگ‌ها ۱۲-۱۴ ساعت",
    },
    {
        "id": 17,
        "section": 5,
        "variable": "stool_consistency",
        "text": "مدفوعش معمولاً چطوریه؟",
        "type": "inline_button",
        "options": [
            {"text": "✅ فرم‌دار و سفت مناسب", "value": "normal"},
            {"text": "💧 شل یا بی‌فرم", "value": "soft"},
            {"text": "🔴 اسهال مکرر", "value": "diarrhea"},
            {"text": "⚫ سفت/یبوست", "value": "hard"},
            {"text": "🔀 متغیر", "value": "variable"},
        ],
        "micro_copy": None,
    },
    {
        "id": 18,
        "section": 5,
        "variable": "water_intake",
        "text": "نسبت به قبل (۲-۳ ماه پیش)، آب خوردنش چه تغییری کرده؟",
        "type": "inline_button",
        "options": [
            {"text": "➖ کمتر شده", "value": "decreased"},
            {"text": "✅ فرقی نکرده", "value": "same"},
            {"text": "➕ بیشتر شده", "value": "increased"},
            {"text": "📈 خیلی بیشتر شده", "value": "much_increased"},
        ],
        "micro_copy": "💡 تغییر ناگهانی آب خوردن می‌تونه علامت مهمی باشه",
    },
    {
        "id": 19,
        "section": 6,
        "variable": "energy_change",
        "text": "انرژی و سرزندگیش نسبت به ۲-۳ ماه پیش چطوره؟",
        "type": "inline_button",
        "options": [
            {"text": "📈 بیشتر/بهتر شده", "value": "increased"},
            {"text": "✅ فرقی نکرده", "value": "same"},
            {"text": "📉 کمتر شده", "value": "decreased"},
            {"text": "📉📉 خیلی کمتر شده", "value": "much_decreased"},
        ],
        "micro_copy": None,
    },
    {
        "id": 20,
        "section": 6,
        "variable": "stress_signs",
        "text": "کدوم یکی از این رفتارها رو داره؟ (می‌تونی چند تا انتخاب کنی)",
        "type": "multi_select",
        "options": [
            {"text": "🚫 هیچکدوم", "value": "none"},
            {"text": "👅 لیسیدن زیاد بدن", "value": "excessive_licking"},
            {"text": "🦷 جویدن پنجه/دم", "value": "chewing"},
            {"text": "🐕 پارس/میو بی‌دلیل", "value": "vocalization"},
            {"text": "🙈 پنهان شدن زیاد", "value": "hiding"},
            {"text": "😰 لرزش/بی‌قراری", "value": "trembling"},
            {"text": "🚽 دستشویی نامناسب", "value": "inappropriate_elimination"},
        ],
        "micro_copy": "💡 بعد از انتخاب، دکمه «تمام» رو بزن",
        "confirm_button": "✅ تمام",
    },
]


def get_question_by_id(question_id):
    for q in QUESTIONS:
        if q["id"] == question_id:
            return q
    return None


def get_total_questions():
    return len(QUESTIONS)
