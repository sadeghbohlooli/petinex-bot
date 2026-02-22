# ============================================================
# Petinex — Pet Health Assessment Questionnaire
# Version: Final Approved (1404/12/03)
# 33 base questions + 8 conditional paths
# ============================================================

WELCOME_MESSAGE = (
    "🐾 <b>به Petinex خوش آمدید!</b>\n\n"
    "سلام! من قراره یه چکاپ هوشمند از وضعیت سلامت پت قشنگت انجام بدم.\n\n"
    "📋 <b>این ارزیابی شامل چیه؟</b>\n"
    "• حدود ۲۵ تا ۳۳ سؤال کوتاه (بسته به پاسخ‌هات)\n"
    "• حدود ۵ تا ۱۰ دقیقه زمان\n"
    "• یک گزارش شخصی‌سازی‌شده علمی\n\n"
    "⚠️ <b>نکته مهم:</b> این ارزیابی جایگزین معاینه دامپزشک نیست، "
    "اما بهت کمک می‌کنه وضعیت کلی رو بهتر بشناسی.\n\n"
    "آماده‌ای شروع کنیم؟ 👇"
)

START_BUTTON_TEXT = "🚀 شروع ارزیابی"

TRANSITIONS = {
    "section_A": "📌 <b>بخش ۱ از ۶: شناسنامه پت</b>\nبذار اول یکم بیشتر باهاش آشنا بشم... 🐾",
    "section_B": "📌 <b>بخش ۲ از ۶: غذا و آب</b>\nحالا بریم سراغ تغذیه‌ش... 🍽️",
    "section_C": "📌 <b>بخش ۳ از ۶: بدن و ظاهر</b>\nیه نگاه به فرم بدنش بندازیم... 🏋️",
    "section_D": "📌 <b>بخش ۴ از ۶: حرکت و انرژی</b>\nببینیم چقدر تحرک و انرژی داره... 🏃",
    "section_E": "📌 <b>بخش ۵ از ۶: علائم هشدار</b>\nیه سری علائم مهم رو چک کنیم... 🚨",
    "section_F": "📌 <b>بخش ۶ از ۶: سوابق پزشکی و تغییرات</b>\nآخرین بخش — سوابق و تغییرات اخیر... 📊",
}

COMPLETION_MESSAGE = (
    "✅ <b>ممنون که وقت گذاشتی!</b>\n\n"
    "گزارش سلامت اختصاصی پتت داره آماده میشه...\n"
    "🕐 تا ۲۴ ساعت آینده برات ارسال میشه.\n\n"
    "اگه سؤالی داشتی، همینجا پیام بده. 🐾"
)

# ============================================================
# QUESTIONS LIST
# ============================================================
#
# Each question dict can have:
#   id              : int — unique question identifier
#   section         : str — "A", "B", "C", "D", "E", "F"
#   variable        : str — key used for storing the answer
#   text            : str — question text shown to user
#   type            : str — "inline_button", "multi_select", "text_input", "number_input"
#   options         : list[dict] | None — button options
#   micro_copy      : str | None — helper text shown below
#   confirm_button  : str | None — for multi_select, the confirm button text
#   condition       : dict | None — when to show this question
#                     e.g. {"variable": "pet_type", "value": ["dog"]}
#                     e.g. {"and": [{"variable": "sex", "value": ["female"]},
#                                   {"variable": "neutered", "value": ["no"]}]}
#   conditional_options : dict | None — different option sets based on a variable
#                     e.g. {"depends_on": "pet_type", "dog": [...], "cat": [...]}
#   has_other_text  : bool — if True, last "other" option opens a text field
#   number_range    : dict | None — for number_input, e.g. {"min": 1, "max": 25}
#   placeholder     : str | None — placeholder for text/number inputs
#   followup_on     : dict | None — sub-question triggered by specific answer
# ============================================================

QUESTIONS = [
    # ================================================================
    # SECTION A: شناسنامه پت (Questions 1–6, conditionals: 4a, 4b, 6a)
    # ================================================================
    {
        "id": 1,
        "section": "A",
        "variable": "pet_name",
        "text": "🏷️ اسم پت قشنگت چیه؟ 💕",
        "type": "text_input",
        "options": None,
        "micro_copy": None,
        "placeholder": "مثلاً: شِرو، ملوس، آریا ...",
        "condition": None,
    },
    {
        "id": 2,
        "section": "A",
        "variable": "pet_type",
        "text": "🐾 همدم خونگی ما سگه یا گربه؟",
        "type": "inline_button",
        "options": [
            {"text": "🐶 سگ", "value": "dog"},
            {"text": "🐱 گربه", "value": "cat"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 3,
        "section": "A",
        "variable": "breed",
        "text": "🧬 نژاد پتت چیه؟",
        "type": "inline_button",
        "options": None,  # Uses conditional_options
        "micro_copy": None,
        "condition": None,
        "has_other_text": True,
        "conditional_options": {
            "depends_on": "pet_type",
            "dog": [
                {"text": "ژرمن شپرد", "value": "german_shepherd"},
                {"text": "گلدن رتریور", "value": "golden_retriever"},
                {"text": "هاسکی", "value": "husky"},
                {"text": "پامرانین", "value": "pomeranian"},
                {"text": "شیتزو", "value": "shih_tzu"},
                {"text": "پودل", "value": "poodle"},
                {"text": "چیواوا", "value": "chihuahua"},
                {"text": "تریر", "value": "terrier"},
                {"text": "دورگه (مشخص نیست)", "value": "mixed"},
                {"text": "نژاد دیگه (خودم می‌نویسم)", "value": "_other"},
            ],
            "cat": [
                {"text": "پرشین (ایرانی)", "value": "persian"},
                {"text": "اسکاتیش", "value": "scottish"},
                {"text": "بریتیش", "value": "british"},
                {"text": "خیابانی (DSH)", "value": "dsh"},
                {"text": "سیامی", "value": "siamese"},
                {"text": "رگدال", "value": "ragdoll"},
                {"text": "مین‌کون", "value": "maine_coon"},
                {"text": "هیمالین", "value": "himalayan"},
                {"text": "دورگه (مشخص نیست)", "value": "mixed"},
                {"text": "نژاد دیگه (خودم می‌نویسم)", "value": "_other"},
            ],
        },
    },
    {
        "id": 4,
        "section": "A",
        "variable": "age_group",
        "text": "📅 پتت تو کدوم بازه سنیه؟",
        "type": "inline_button",
        "options": [
            {"text": "🐣 زیر ۶ ماه (توله/بچه‌گربه)", "value": "under_6m"},
            {"text": "🐶 ۶ ماه تا ۱ سال (نوجوون)", "value": "6m_to_1y"},
            {"text": "🐕 ۱ تا ۳ سال (جوون)", "value": "1y_to_3y"},
            {"text": "🐕‍🦺 ۳ تا ۷ سال (بالغ)", "value": "3y_to_7y"},
            {"text": "👴 ۷ تا ۱۰ سال (میان‌سال)", "value": "7y_to_10y"},
            {"text": "🦮 بالای ۱۰ سال (سالمند)", "value": "above_10y"},
            {"text": "🤷 نمی‌دونم", "value": "unknown"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    # --- Conditional 4a: age detail under 1 year ---
    {
        "id": "4a",
        "section": "A",
        "variable": "age_months_detail",
        "text": "📅 تقریباً چند ماهشه؟",
        "type": "inline_button",
        "options": [
            {"text": "کمتر از ۲ ماه", "value": "lt_2m"},
            {"text": "۲ تا ۴ ماه", "value": "2m_to_4m"},
            {"text": "۴ تا ۶ ماه", "value": "4m_to_6m"},
            {"text": "۶ تا ۹ ماه", "value": "6m_to_9m"},
            {"text": "۹ تا ۱۲ ماه", "value": "9m_to_12m"},
        ],
        "micro_copy": None,
        "condition": {
            "variable": "age_group",
            "value": ["under_6m", "6m_to_1y"],
        },
    },
    # --- Conditional 4b: age detail over 1 year ---
    {
        "id": "4b",
        "section": "A",
        "variable": "age_years_detail",
        "text": "📅 تقریباً چند سالشه؟",
        "type": "number_input",
        "options": None,
        "micro_copy": None,
        "placeholder": "مثلاً: 3",
        "number_range": {"min": 1, "max": 25},
        "condition": {
            "variable": "age_group",
            "value": ["1y_to_3y", "3y_to_7y", "7y_to_10y", "above_10y"],
        },
    },
    {
        "id": 5,
        "section": "A",
        "variable": "sex",
        "text": "⚧️ پتت نره یا ماده؟",
        "type": "inline_button",
        "options": [
            {"text": "♂️ نر", "value": "male"},
            {"text": "♀️ ماده", "value": "female"},
            {"text": "🤷 نمی‌دونم", "value": "unknown"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 6,
        "section": "A",
        "variable": "neutered",
        "text": "✂️ آیا پتت عقیم شده؟",
        "type": "inline_button",
        "options": [
            {"text": "✅ بله، عقیم شده", "value": "yes"},
            {"text": "❌ نه، عقیم نشده", "value": "no"},
            {"text": "🤷 نمی‌دونم", "value": "unknown"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    # --- Conditional 6a: pregnancy/nursing ---
    {
        "id": "6a",
        "section": "A",
        "variable": "pregnancy_status",
        "text": "🤱 آیا پتت الان باردار هست یا تو دوران شیردهی؟",
        "type": "inline_button",
        "options": [
            {"text": "🤰 بله، باردار هست", "value": "pregnant"},
            {"text": "🍼 بله، داره شیر میده", "value": "nursing"},
            {"text": "❌ نه، هیچ‌کدوم", "value": "none"},
            {"text": "🤷 مطمئن نیستم", "value": "unsure"},
        ],
        "micro_copy": None,
        "condition": {
            "and": [
                {"variable": "sex", "value": ["female"]},
                {"variable": "neutered", "value": ["no"]},
            ]
        },
    },

    # ================================================================
    # SECTION B: غذا و آب (Questions 7–13, conditionals: 7a, 7b)
    # ================================================================
    {
        "id": 7,
        "section": "B",
        "variable": "food_type",
        "text": "🥣 غذای اصلی پتت — چیزی که بیشترین حجم رو تشکیل میده — چیه؟",
        "type": "inline_button",
        "options": [
            {"text": "🥫 غذای خشک", "value": "dry"},
            {"text": "🥘 کنسرو / پوچ", "value": "wet"},
            {"text": "🔀 ترکیبی", "value": "mixed"},
            {"text": "🍖 غذای پخته خونگی", "value": "homemade"},
            {"text": "🥩 غذای خام", "value": "raw"},
            {"text": "🍚 بیشتر از غذای خودمون (برنج، مرغ سفره و...)", "value": "table_food"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    # --- Conditional 7a: food brand ---
    {
        "id": "7a",
        "section": "B",
        "variable": "food_brand",
        "text": "🏪 بیشتر از چه برندی استفاده می‌کنی؟",
        "type": "inline_button",
        "options": None,  # Uses conditional_options
        "micro_copy": None,
        "has_other_text": True,
        "condition": {
            "variable": "food_type",
            "value": ["dry", "wet", "mixed"],
        },
        "conditional_options": {
            "depends_on": "pet_type",
            "dog": [
                {"text": "رویال کنین (Royal Canin)", "value": "royal_canin"},
                {"text": "هپی داگ (Happy Dog)", "value": "happy_dog"},
                {"text": "جوسرا (Josera)", "value": "josera"},
                {"text": "پروپلن (Pro Plan)", "value": "pro_plan"},
                {"text": "رفلکس (Reflex)", "value": "reflex"},
                {"text": "نوتری (Nutri Pet)", "value": "nutri_pet"},
                {"text": "مفید (Mofeed)", "value": "mofeed"},
                {"text": "سیمبا (Simba)", "value": "simba"},
                {"text": "برند دیگه (خودم می‌نویسم)", "value": "_other"},
                {"text": "نمی‌دونم / بدون برند خاص", "value": "unknown"},
            ],
            "cat": [
                {"text": "رویال کنین (Royal Canin)", "value": "royal_canin"},
                {"text": "هپی کت (Happy Cat)", "value": "happy_cat"},
                {"text": "جوسرا (Josera)", "value": "josera"},
                {"text": "پروپلن (Pro Plan)", "value": "pro_plan"},
                {"text": "رفلکس (Reflex)", "value": "reflex"},
                {"text": "ویسکاس (Whiskas)", "value": "whiskas"},
                {"text": "شبا (Sheba)", "value": "sheba"},
                {"text": "نوتری (Nutri Pet)", "value": "nutri_pet"},
                {"text": "مفید (Mofeed)", "value": "mofeed"},
                {"text": "سیمبا (Simba)", "value": "simba"},
                {"text": "برند دیگه (خودم می‌نویسم)", "value": "_other"},
                {"text": "نمی‌دونم / بدون برند خاص", "value": "unknown"},
            ],
        },
    },
    # --- Conditional 7b: mixed food details ---
    {
        "id": "7b",
        "section": "B",
        "variable": "mixed_food_details",
        "text": "🔀 می‌تونی بگی دقیقاً چه ترکیبی بهش میدی و چطوری تقسیمش می‌کنی؟",
        "type": "text_input",
        "options": None,
        "micro_copy": None,
        "placeholder": "مثلاً: صبح خشک میدم، شب کنسرو / یا خشک قاطی با مرغ پخته ...",
        "condition": {
            "variable": "food_type",
            "value": ["mixed"],
        },
    },
    {
        "id": 8,
        "section": "B",
        "variable": "meals_per_day",
        "text": "🕐 روزی چند وعده غذا می‌خوره؟",
        "type": "inline_button",
        "options": [
            {"text": "۱ وعده", "value": "1"},
            {"text": "۲ وعده", "value": "2"},
            {"text": "۳ وعده", "value": "3"},
            {"text": "۴ وعده یا بیشتر", "value": "4plus"},
            {"text": "آزاد (همیشه غذا در دسترسشه)", "value": "free"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 9,
        "section": "B",
        "variable": "portion_size",
        "text": "⚖️ تقریباً هر وعده چقدر غذا می‌خوره؟",
        "type": "inline_button",
        "options": [
            {"text": "کمتر از ۵۰ گرم", "value": "lt_50g"},
            {"text": "۵۰ تا ۱۰۰ گرم", "value": "50_100g"},
            {"text": "۱۰۰ تا ۲۰۰ گرم", "value": "100_200g"},
            {"text": "۲۰۰ تا ۴۰۰ گرم", "value": "200_400g"},
            {"text": "بالای ۴۰۰ گرم", "value": "gt_400g"},
            {"text": "نمیدونم دقیقاً", "value": "unknown"},
        ],
        "micro_copy": "💡 حدودی بزن، لازم نیست دقیق باشه",
        "condition": None,
    },
    {
        "id": 10,
        "section": "B",
        "variable": "last_meal_event",
        "text": "🍽️ آخرین وعده غذایی که جلوش گذاشتی، چی شد؟",
        "type": "inline_button",
        "options": [
            {"text": "🐺 تا آخر خورد و هنوز دنبال غذا بود", "value": "ate_all_wanted_more"},
            {"text": "✅ تا آخر خورد، رفت سراغ کارش", "value": "ate_all_done"},
            {"text": "🔸 یکم خورد، بقیه‌ش موند", "value": "ate_some"},
            {"text": "❌ اصلاً نخورد / بو کرد و رفت", "value": "refused"},
            {"text": "🤢 خورد ولی بعدش بالا آورد", "value": "ate_vomited"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 11,
        "section": "B",
        "variable": "treats_extras",
        "text": "🦴 بیرون از وعده غذای اصلی، دیروز چی بهش رسید؟ (همه مواردی که صدق می‌کنه رو بزن)",
        "type": "multi_select",
        "options": [
            {"text": "🚫 هیچی — فقط غذای اصلی", "value": "nothing"},
            {"text": "🦴 تشویقی/اسنک مخصوص حیوان", "value": "pet_treats"},
            {"text": "🧀 تکه‌های غذای خودمون (پنیر، مرغ، نون...)", "value": "human_food_pieces"},
            {"text": "🍖 استخون یا خرده غذا از سفره", "value": "bones_scraps"},
            {"text": "🥛 شیر یا ماست", "value": "dairy"},
            {"text": "🤷 دقیق یادم نیست", "value": "dont_remember"},
        ],
        "micro_copy": "💡 بعد از انتخاب، دکمه «تمام» رو بزن",
        "confirm_button": "✅ تمام",
        "condition": None,
    },
    {
        "id": 12,
        "section": "B",
        "variable": "food_allergy",
        "text": "⚠️ تا حالا پتت به ماده غذایی خاصی حساسیت نشون داده؟",
        "type": "inline_button",
        "options": [
            {"text": "😊 نه، تا حالا مشکلی نداشته", "value": "no_allergy"},
            {"text": "🐔 آره، به یه پروتئین خاص (مثلاً مرغ، گوشت قرمز، ماهی)", "value": "protein_allergy"},
            {"text": "🌾 آره، به غلات (مثلاً گندم، ذرت)", "value": "grain_allergy"},
            {"text": "🥛 آره، به لبنیات", "value": "dairy_allergy"},
            {"text": "🤔 فکر می‌کنم آره، ولی دقیق نمی‌دونم به چی", "value": "suspected_allergy"},
            {"text": "🤷 مطمئن نیستم", "value": "unsure"},
            {"text": "✏️ سایر (لطفاً بنویسید)", "value": "_other"},
        ],
        "micro_copy": None,
        "has_other_text": True,
        "condition": None,
    },
    {
        "id": 13,
        "section": "B",
        "variable": "water_intake",
        "text": "💧 پتت نسبت به قبل چقدر آب می‌خوره؟",
        "type": "inline_button",
        "options": [
            {"text": "📈 بیشتر از قبل", "value": "increased"},
            {"text": "✅ مثل همیشه — تغییری نکرده", "value": "same"},
            {"text": "📉 کمتر از قبل", "value": "decreased"},
            {"text": "🤷 راستش دقت نکردم", "value": "not_noticed"},
        ],
        "micro_copy": None,
        "condition": None,
    },

    # ================================================================
    # SECTION C: بدن و ظاهر (Questions 14–17)
    # ================================================================
    {
        "id": 14,
        "section": "C",
        "variable": "ribs_feel",
        "text": (
            "🖐️ <b>الان یه کار ساده بکن:</b> دستت رو آروم روی پهلوی پتت بکش. "
            "چی حس کردی؟"
        ),
        "type": "inline_button",
        "options": [
            {"text": "🦴 دنده‌ها واضح دیدم، بدون لمس", "value": "very_thin"},
            {"text": "👆 با کشیدن دست، راحت حسشون کردم", "value": "ideal"},
            {"text": "🤏 مجبور شدم فشار بدم تا حسشون کنم", "value": "overweight"},
            {"text": "❌ هرچی فشار دادم حس نشد، یه لایه نرم روشه", "value": "obese"},
            {"text": "🐈 نمیذاره دست بزنم", "value": "cant_touch"},
        ],
        "micro_copy": "💡 مثل پشت دست خودت رو لمس کنی — اگه استخون‌ها به راحتی حس بشن، وزنش مناسبه",
        "condition": None,
    },
    {
        "id": 15,
        "section": "C",
        "variable": "waist_shape",
        "text": (
            "👁️ <b>از بالا نگاه کن</b> (بالای سر پتت بایست و پایین رو نگاه کن). "
            "ناحیه کمر و شکمش چه شکلیه؟"
        ),
        "type": "inline_button",
        "options": [
            {"text": "⌛ مثل ساعت شنی — گودی کمر واضحه", "value": "hourglass"},
            {"text": "📏 تقریباً صاف — یکم گودی داره", "value": "slight_waist"},
            {"text": "🥚 بیضی/گرد — شکم از پهلوها زده بیرون", "value": "oval_round"},
            {"text": "🤷 نمی‌تونم تشخیص بدم (موهاش بلنده / نمیذاره)", "value": "cant_tell"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 16,
        "section": "C",
        "variable": "weight_knowledge",
        "text": "⚖️ وزن دقیق پتت رو می‌دونی؟",
        "type": "inline_button",
        "options": [
            {"text": "✏️ بله، می‌نویسم (kg)", "value": "knows_exact"},
            {"text": "📏 دقیق نمی‌دونم، یه تخمین بزنم", "value": "estimate"},
            {"text": "🤷 اصلاً نمی‌دونم", "value": "dont_know"},
        ],
        "micro_copy": None,
        "condition": None,
        # Sub-flow handled in bot logic:
        # if "knows_exact" or "estimate" → ask for number_input (weight_kg)
        # if "dont_know" → ask weight_feel question
    },
    # --- Sub-question 16 → weight in kg (if knows or estimates) ---
    {
        "id": "16_kg",
        "section": "C",
        "variable": "weight_kg",
        "text": "⚖️ وزنش رو بنویس (کیلوگرم):",
        "type": "number_input",
        "options": None,
        "micro_copy": "💡 مثلاً: 4.5",
        "placeholder": "مثلاً: 4.5",
        "number_range": {"min": 0.1, "max": 120},
        "condition": {
            "variable": "weight_knowledge",
            "value": ["knows_exact", "estimate"],
        },
    },
    # --- Sub-question 16 → weight feel (if doesn't know) ---
    {
        "id": "16_feel",
        "section": "C",
        "variable": "weight_feel",
        "text": "اشکال نداره! وقتی بلندش می‌کنی چه حسی داری؟",
        "type": "inline_button",
        "options": [
            {"text": "🪶 خیلی سبکه (مثل بالش)", "value": "very_light"},
            {"text": "🐕 یه وزنی داره ولی راحت بلند میشه", "value": "moderate"},
            {"text": "🏋️ سنگینه، به‌سختی بلند میشه", "value": "heavy"},
            {"text": "🐘 نمیشه بلندش کرد", "value": "cant_lift"},
        ],
        "micro_copy": None,
        "condition": {
            "variable": "weight_knowledge",
            "value": ["dont_know"],
        },
    },
    {
        "id": 17,
        "section": "C",
        "variable": "skin_coat",
        "text": "🔍 <b>الان یه نگاه به بدن پتت بنداز.</b> کدوم مورد رو می‌بینی؟ (همه موارد رو بزن)",
        "type": "multi_select",
        "options": [
            {"text": "✅ موها براق و مرتبه، پوست تمیزه", "value": "healthy"},
            {"text": "🧹 ریزش مو بیشتر از معمول", "value": "excessive_shedding"},
            {"text": "🔴 یه‌جایی رو زیاد می‌خارونه یا لیس می‌زنه", "value": "itching"},
            {"text": "⚫ پوسته/شوره داره", "value": "dandruff"},
            {"text": "🩹 زخم، ورم، یا تیکه بدون مو دارم می‌بینم", "value": "wound_bald"},
            {"text": "🐈 نمی‌تونم ببینم (مو خیلی بلنده / نمیذاره)", "value": "cant_see"},
        ],
        "micro_copy": "💡 بعد از انتخاب، دکمه «تمام» رو بزن",
        "confirm_button": "✅ تمام",
        "condition": None,
    },

    # ================================================================
    # SECTION D: حرکت و انرژی (Questions 18–20)
    # ================================================================
    {
        "id": 18,
        "section": "D",
        "variable": "greeting_energy",
        "text": "🚪 وقتی از بیرون میای خونه یا صبح بیدار میشی، پتت چه واکنشی نشون میده؟",
        "type": "inline_button",
        "options": [
            {"text": "🎉 میاد سمتم، ذوق می‌کنه، دُم تکون میده / دورم می‌چرخه", "value": "excited"},
            {"text": "🐕 میاد ولی آروم‌تر از قبل", "value": "calm_approach"},
            {"text": "😐 سرشو بلند می‌کنه / نگاه می‌کنه ولی بلند نمیشه", "value": "head_lift_only"},
            {"text": "😴 اصلاً واکنش نشون نمیده", "value": "no_reaction"},
            {"text": "🆕 تازه گرفتمش، هنوز نمی‌شناسمش", "value": "new_pet"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 19,
        "section": "D",
        "variable": "daily_activity",
        "text": "🏃 دیروز (یا آخرین روز عادی)، پتت چقدر حرکت فعال داشت؟",
        "type": "inline_button",
        "options": [
            {"text": "🚫 تقریباً هیچی — بیشتر خوابید یا دراز کشید", "value": "none"},
            {"text": "🚶 یه پیاده‌روی کوتاه یا بازی کم (زیر ۱۵ دقیقه)", "value": "light"},
            {"text": "🏃 پیاده‌روی یا بازی متوسط (۱۵ تا ۴۵ دقیقه)", "value": "moderate"},
            {"text": "🏃‍♂️💨 فعالیت زیاد — دوید، بازی شدید (بالای ۴۵ دقیقه)", "value": "high"},
            {"text": "🐈 گربمه، خودش بازی می‌کنه — نمی‌تونم بگم چقدر", "value": "cat_self_play"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 20,
        "section": "D",
        "variable": "living_space",
        "text": "🏠 پتت بیشتر وقتش رو کجا میگذرونه؟",
        "type": "inline_button",
        "options": [
            {"text": "🏢 آپارتمان — بدون دسترسی به فضای باز", "value": "apartment_no_outdoor"},
            {"text": "🏠 آپارتمان/خونه — با بالکن یا تراس", "value": "apartment_balcony"},
            {"text": "🏡 خونه ویلایی با حیاط", "value": "house_yard"},
            {"text": "🌳 بیشتر بیرون (حیاط/باغ/مزرعه)", "value": "mostly_outdoor"},
        ],
        "micro_copy": None,
        "condition": None,
    },

    # ================================================================
    # SECTION E: علائم هشدار (Questions 21–25)
    # ================================================================
    {
        "id": 21,
        "section": "E",
        "variable": "stool_consistency",
        "text": "💩 آخرین باری که مدفوع پتت رو دیدی یا جمع کردی، چطوری بود؟",
        "type": "inline_button",
        "options": [
            {"text": "🟤 سفت و شکل‌دار — راحت جمع شد", "value": "firm_formed"},
            {"text": "🟡 نرم ولی شکل داشت", "value": "soft_formed"},
            {"text": "🧈 خمیری — به زمین چسبید", "value": "mushy"},
            {"text": "💧 آبکی — نشد جمعش کنم", "value": "watery"},
            {"text": "🔴 خون یا چیز غیرعادی توش دیدم", "value": "blood_abnormal"},
            {"text": "❓ چند روزه ندیدم", "value": "not_seen"},
        ],
        "micro_copy": "💡 «چند روزه ندیدم» ممکنه نشونه یبوست باشه — مهمه!",
        "condition": None,
    },
    {
        "id": 22,
        "section": "E",
        "variable": "vomiting",
        "text": "🤢 تو ۲ هفته گذشته، پتت استفراغ کرده؟",
        "type": "inline_button",
        "options": [
            {"text": "✅ نه، اصلاً", "value": "none"},
            {"text": "🔸 ۱-۲ بار — غذای هضم‌نشده یا علف", "value": "1_2_times"},
            {"text": "🔶 ۳+ بار", "value": "3plus_times"},
            {"text": "🟡 مایع زرد/کف‌دار بالا آورده", "value": "yellow_foam"},
            {"text": "🔴 خون یا چیز عجیب توش بود", "value": "blood_abnormal"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 23,
        "section": "E",
        "variable": "urination",
        "text": "🚽 تو ۱ هفته اخیر، چیز غیرعادی تو ادرار پتت دیدی؟",
        "type": "inline_button",
        "options": [
            {"text": "✅ نه، همه‌چیز عادیه", "value": "normal"},
            {"text": "🔸 بیشتر از قبل ادرار می‌کنه", "value": "more_frequent"},
            {"text": "🔶 تو خونه ادرار کرده (قبلاً نمی‌کرد)", "value": "indoor_accident"},
            {"text": "🟡 رنگش تیره‌ست یا بوی شدید داره", "value": "dark_smelly"},
            {"text": "🔴 زور می‌زنه ولی کم میاد", "value": "straining"},
            {"text": "🤷 دقت نکردم", "value": "not_noticed"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 24,
        "section": "E",
        "variable": "limping_mobility",
        "text": "🦿 تو هفته اخیر، موقع راه‌رفتن یا بلند شدن پتت، چیز غیرعادی دیدی؟",
        "type": "inline_button",
        "options": [
            {"text": "✅ نه، عادی راه میره و حرکت می‌کنه", "value": "normal"},
            {"text": "🔸 یکم سخت بلند میشه ولی بعدش عادیه", "value": "slow_start"},
            {"text": "🔶 یه پاش رو کمتر زمین میذاره (لنگ)", "value": "limping"},
            {"text": "🔴 واضح درد داره / ناله می‌کنه", "value": "pain"},
            {"text": "🐈 گربمه — کمتر می‌پره (جایی که قبلاً می‌پرید)", "value": "cat_less_jumping"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 25,
        "section": "E",
        "variable": "face_check",
        "text": "👁️ یه نگاه سریع به صورت پتت بنداز. کدوم مورد رو می‌بینی؟ (چندتا بزن)",
        "type": "multi_select",
        "options": [
            {"text": "✅ همه‌چیز تمیز و عادیه", "value": "all_normal"},
            {"text": "👁️ ترشح یا قرمزی چشم", "value": "eye_discharge"},
            {"text": "👂 بوی بد یا ترشح از گوش", "value": "ear_issue"},
            {"text": "🦷 بوی بد دهان", "value": "bad_breath"},
            {"text": "🤧 عطسه یا آبریزش بینی", "value": "sneezing"},
            {"text": "😢 اشک‌ریزش زیاد / لکه زیر چشم", "value": "tear_staining"},
        ],
        "micro_copy": "💡 بعد از انتخاب، دکمه «تمام» رو بزن",
        "confirm_button": "✅ تمام",
        "condition": None,
    },

    # ================================================================
    # SECTION F: سوابق پزشکی + دارو/مکمل + تغییرات (Questions 26–33)
    # Conditionals: 27a, 28a, 30a
    # ================================================================
    {
        "id": 26,
        "section": "F",
        "variable": "medical_history",
        "text": "🏥 آیا دامپزشک تا حالا بیماری خاصی برای پتت تشخیص داده یا زمینه بیماری خاصی داره؟",
        "type": "multi_select",
        "options": None,  # Uses conditional_options
        "micro_copy": "💡 می‌تونی چند مورد انتخاب کنی. اگه سابقه‌ای نداره «هیچ‌کدام» رو بزن",
        "confirm_button": "✅ تمام",
        "has_other_text": True,
        "condition": None,
        "conditional_options": {
            "depends_on": "pet_type",
            "dog": [
                {"text": "بیماری پوستی (حساسیت/درماتیت/قارچ)", "value": "skin_disease"},
                {"text": "مشکل گوارشی مزمن (حساسیت غذایی)", "value": "chronic_gi"},
                {"text": "بیماری کلیوی", "value": "kidney"},
                {"text": "دیابت", "value": "diabetes"},
                {"text": "مشکل قلبی", "value": "heart"},
                {"text": "صرع / تشنج", "value": "epilepsy"},
                {"text": "مشکل مفصلی (آرتروز/دیسپلازی)", "value": "joint"},
                {"text": "تومور / سرطان", "value": "tumor"},
                {"text": "کم‌کاری تیروئید", "value": "hypothyroid"},
                {"text": "سنگ مثانه / مشکل ادراری", "value": "urinary"},
                {"text": "هیچ‌کدام / سابقه بیماری خاصی نداره", "value": "none"},
                {"text": "سایر (خودم می‌نویسم)", "value": "_other"},
            ],
            "cat": [
                {"text": "بیماری کلیوی مزمن (CKD)", "value": "ckd"},
                {"text": "بیماری مجرای ادراری (FLUTD)", "value": "flutd"},
                {"text": "دیابت", "value": "diabetes"},
                {"text": "پرکاری تیروئید", "value": "hyperthyroid"},
                {"text": "بیماری قلبی (HCM)", "value": "hcm"},
                {"text": "آسم / مشکل تنفسی", "value": "asthma"},
                {"text": "بیماری پوستی (حساسیت/قارچ)", "value": "skin_disease"},
                {"text": "FIV (ایدز گربه‌ای)", "value": "fiv"},
                {"text": "FeLV (لوکمی گربه‌ای)", "value": "felv"},
                {"text": "مشکل دندان / لثه", "value": "dental"},
                {"text": "هیچ‌کدام / سابقه بیماری خاصی نداره", "value": "none"},
                {"text": "سایر (خودم می‌نویسم)", "value": "_other"},
            ],
        },
    },
    {
        "id": 27,
        "section": "F",
        "variable": "on_medication",
        "text": "💊 الان پتت داروی خاصی مصرف می‌کنه؟",
        "type": "inline_button",
        "options": [
            {"text": "❌ نه", "value": "no"},
            {"text": "💊 بله، دارو داره", "value": "yes"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    # --- Conditional 27a: medication details ---
    {
        "id": "27a",
        "section": "F",
        "variable": "medication_details",
        "text": "📝 اسم حدودی داروها و اینکه برای چی هستن رو بنویس (اگه می‌دونی):",
        "type": "text_input",
        "options": None,
        "micro_copy": None,
        "placeholder": "مثلاً: قرص ضد انگل ماهیانه، آنتی‌بیوتیک برای عفونت پوستی، قرص قلب ...",
        "condition": {
            "variable": "on_medication",
            "value": ["yes"],
        },
    },
    {
        "id": 28,
        "section": "F",
        "variable": "on_supplements",
        "text": "🧴 مکمل هم بهش می‌دی؟ (مثل ویتامین، امگا۳، مفصل و...)",
        "type": "inline_button",
        "options": [
            {"text": "❌ نه", "value": "no"},
            {"text": "✅ بله", "value": "yes"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    # --- Conditional 28a: supplement details ---
    {
        "id": "28a",
        "section": "F",
        "variable": "supplement_details",
        "text": "📝 اسم و نوع مکمل‌هایی که بهش میدی رو بنویس:",
        "type": "text_input",
        "options": None,
        "micro_copy": None,
        "placeholder": "مثلاً: امگا۳ برای پوست و مو، گلوکزامین برای مفصل، مولتی‌ویتامین ...",
        "condition": {
            "variable": "on_supplements",
            "value": ["yes"],
        },
    },
    {
        "id": 29,
        "section": "F",
        "variable": "last_vet_visit",
        "text": "🩺 آخرین بار کِی پتت رو بردی دامپزشکی؟",
        "type": "inline_button",
        "options": [
            {"text": "📅 کمتر از ۱ ماه پیش", "value": "lt_1month"},
            {"text": "📅 ۱ تا ۳ ماه پیش", "value": "1_3months"},
            {"text": "📅 ۳ تا ۶ ماه پیش", "value": "3_6months"},
            {"text": "📅 ۶ ماه تا ۱ سال پیش", "value": "6m_1year"},
            {"text": "📅 بیشتر از ۱ سال پیش", "value": "gt_1year"},
            {"text": "❌ تا حالا نبردم", "value": "never"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 30,
        "section": "F",
        "variable": "vaccination_status",
        "text": "💉 وضعیت واکسیناسیون پتت چطوره؟",
        "type": "inline_button",
        "options": [
            {"text": "✅ کامل و به‌روزه", "value": "complete"},
            {"text": "⚠️ یه سری رو زده ولی کامل نیست", "value": "partial"},
            {"text": "❌ هنوز واکسن نزده", "value": "none"},
            {"text": "🤷 نمی‌دونم / مطمئن نیستم", "value": "unknown"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    # --- Conditional 30a: vaccination details ---
    {
        "id": "30a",
        "section": "F",
        "variable": "vaccination_details",
        "text": "💉 کدوم واکسن‌ها رو تا الان زده؟ (می‌تونی چندتا انتخاب کنی)",
        "type": "multi_select",
        "options": None,  # Uses conditional_options
        "micro_copy": "💡 بعد از انتخاب، دکمه «تمام» رو بزن",
        "confirm_button": "✅ تمام",
        "condition": {
            "variable": "vaccination_status",
            "value": ["complete", "partial"],
        },
        "conditional_options": {
            "depends_on": "pet_type",
            "dog": [
                {"text": "💚 واکسن چندگانه (۵ گانه / ۷ گانه)", "value": "polyvalent"},
                {"text": "🔴 هاری", "value": "rabies"},
                {"text": "🟤 ضدکرم / انگل‌زدایی", "value": "deworming"},
                {"text": "⬜ هیچ‌کدوم", "value": "none"},
                {"text": "🤷 نمی‌دونم دقیقاً چیا زده", "value": "unknown"},
            ],
            "cat": [
                {"text": "💚 واکسن سه‌گانه", "value": "fvrcp"},
                {"text": "🔴 هاری", "value": "rabies"},
                {"text": "💛 لوکمی", "value": "felv_vaccine"},
                {"text": "🟤 ضدکرم / انگل‌زدایی", "value": "deworming"},
                {"text": "⬜ هیچ‌کدوم", "value": "none"},
                {"text": "🤷 نمی‌دونم دقیقاً چیا زده", "value": "unknown"},
            ],
        },
    },
    {
        "id": 31,
        "section": "F",
        "variable": "weight_change_trend",
        "text": "⚖️ نسبت به ۲-۳ ماه پیش، به نظرت وزن پتت چه تغییری کرده؟",
        "type": "inline_button",
        "options": [
            {"text": "📉 لاغرتر شده", "value": "lost_weight"},
            {"text": "✅ فرقی نکرده", "value": "same"},
            {"text": "📈 چاق‌تر شده", "value": "gained_weight"},
            {"text": "🆕 تازه گرفتمش، نمی‌تونم مقایسه کنم", "value": "new_pet"},
        ],
        "micro_copy": None,
        "condition": None,
    },
    {
        "id": 32,
        "section": "F",
        "variable": "recent_changes",
        "text": "🔄 آیا این ۲ هفته اخیر تغییر خاصی تو زندگی پتت بوده؟ (همه موارد رو بزن)",
        "type": "multi_select",
        "options": [
            {"text": "🏠 تغییر محل زندگی / اسباب‌کشی", "value": "moved"},
            {"text": "🍽️ تغییر نوع یا برند غذا", "value": "food_change"},
            {"text": "💊 شروع دارو یا مکمل جدید", "value": "new_med"},
            {"text": "🐾 اضافه شدن پت جدید به خونه", "value": "new_pet"},
            {"text": "👶 اضافه شدن عضو جدید به خانواده", "value": "new_family_member"},
            {"text": "😰 استرس خاص (صدای بلند/ترقه/مهمان)", "value": "stress"},
            {"text": "✅ نه، تغییر خاصی نبوده", "value": "none"},
        ],
        "micro_copy": "💡 بعد از انتخاب، دکمه «تمام» رو بزن",
        "confirm_button": "✅ تمام",
        "condition": None,
    },
    {
        "id": 33,
        "section": "F",
        "variable": "open_concern",
        "text": (
            "💬 اگه یه چیز هست که نگرانت کرده یا تغییری دیدی، اینجا بنویس. "
            "هر چیزی — حتی اگه فکر می‌کنی مهم نیست:"
        ),
        "type": "text_input",
        "options": [
            {"text": "✅ نگرانی خاصی ندارم", "value": "no_concern"},
        ],
        "micro_copy": None,
        "placeholder": 'مثلاً: "شب‌ها بی‌قراره"، "دُمش رو گاز می‌گیره"، "بوی بدی میده" ...',
        "condition": None,
        # Special: user can either type text OR press the "no concern" button
    },
]


# ============================================================
# QUESTION FLOW ORDER
# ============================================================
# This defines the exact sequence in which questions are asked.
# Conditional questions are inserted right after their trigger.
# The bot engine should evaluate conditions at runtime.

QUESTION_FLOW = [
    # --- Section A: شناسنامه پت ---
    1,       # pet_name
    2,       # pet_type
    3,       # breed (conditional_options based on pet_type)
    4,       # age_group
    "4a",    # age_months_detail (conditional: under_6m / 6m_to_1y)
    "4b",    # age_years_detail (conditional: 1y+ groups)
    5,       # sex
    6,       # neutered
    "6a",    # pregnancy_status (conditional: female + not neutered)
    # --- Section B: غذا و آب ---
    7,       # food_type
    "7a",    # food_brand (conditional: dry/wet/mixed)
    "7b",    # mixed_food_details (conditional: mixed)
    8,       # meals_per_day
    9,       # portion_size
    10,      # last_meal_event
    11,      # treats_extras (multi_select)
    12,      # food_allergy
    13,      # water_intake
    # --- Section C: بدن و ظاهر ---
    14,      # ribs_feel (BCS)
    15,      # waist_shape
    16,      # weight_knowledge
    "16_kg",   # weight_kg (conditional: knows/estimate)
    "16_feel", # weight_feel (conditional: dont_know)
    17,      # skin_coat (multi_select)
    # --- Section D: حرکت و انرژی ---
    18,      # greeting_energy
    19,      # daily_activity
    20,      # living_space
    # --- Section E: علائم هشدار ---
    21,      # stool_consistency
    22,      # vomiting
    23,      # urination
    24,      # limping_mobility
    25,      # face_check (multi_select)
    # --- Section F: سوابق پزشکی + تغییرات ---
    26,      # medical_history (multi_select, conditional_options)
    27,      # on_medication
    "27a",   # medication_details (conditional: yes)
    28,      # on_supplements
    "28a",   # supplement_details (conditional: yes)
    29,      # last_vet_visit
    30,      # vaccination_status
    "30a",   # vaccination_details (conditional: complete/partial)
    31,      # weight_change_trend
    32,      # recent_changes (multi_select)
    33,      # open_concern
]

# Section boundaries for transition messages
SECTION_BOUNDARIES = {
    "A": 1,       # First question of section A
    "B": 7,       # First question of section B
    "C": 14,      # First question of section C
    "D": 18,      # First question of section D
    "E": 21,      # First question of section E
    "F": 26,      # First question of section F
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_question_by_id(question_id):
    """Get a question dict by its id (int or str like '4a')."""
    for q in QUESTIONS:
        if q["id"] == question_id:
            return q
    return None


def get_total_base_questions():
    """Return count of base (non-conditional) questions."""
    return len([q for q in QUESTIONS if q.get("condition") is None])


def get_total_all_questions():
    """Return total count including conditional questions."""
    return len(QUESTIONS)


def get_options_for_question(question, user_answers):
    """
    Return the correct options list for a question,
    resolving conditional_options based on user's previous answers.
    """
    if "conditional_options" in question and question.get("conditional_options"):
        cond = question["conditional_options"]
        depends_on_var = cond["depends_on"]
        user_value = user_answers.get(depends_on_var)
        if user_value and user_value in cond:
            return cond[user_value]
        # Fallback: return first available option set
        for key in cond:
            if key != "depends_on":
                return cond[key]
    return question.get("options")


def should_show_question(question, user_answers):
    """
    Evaluate whether a conditional question should be shown
    based on user's previous answers.

    Returns True if question has no condition or condition is met.
    """
    condition = question.get("condition")
    if condition is None:
        return True

    # AND condition: all sub-conditions must be true
    if "and" in condition:
        for sub_cond in condition["and"]:
            var = sub_cond["variable"]
            allowed_values = sub_cond["value"]
            user_val = user_answers.get(var)
            if user_val not in allowed_values:
                return False
        return True

    # OR condition (implicit): variable must match one of the values
    if "or" in condition:
        for sub_cond in condition["or"]:
            var = sub_cond["variable"]
            allowed_values = sub_cond["value"]
            user_val = user_answers.get(var)
            if user_val in allowed_values:
                return True
        return False

    # Simple condition
    var = condition["variable"]
    allowed_values = condition["value"]
    user_val = user_answers.get(var)
    return user_val in allowed_values


def get_next_question_id(current_id, user_answers):
    """
    Given the current question id and user's answers so far,
    return the next question id to show (skipping conditionals
    whose conditions aren't met), or None if assessment is complete.
    """
    try:
        current_index = QUESTION_FLOW.index(current_id)
    except ValueError:
        return None

    for i in range(current_index + 1, len(QUESTION_FLOW)):
        next_id = QUESTION_FLOW[i]
        q = get_question_by_id(next_id)
        if q and should_show_question(q, user_answers):
            return next_id

    return None  # Assessment complete


def get_section_for_question(question_id):
    """Return the section letter for a question id."""
    q = get_question_by_id(question_id)
    if q:
        return q["section"]
    return None


def get_section_transition(section):
    """Return the transition message for a section, if any."""
    key = f"section_{section}"
    return TRANSITIONS.get(key)


def should_show_section_transition(question_id, prev_question_id, user_answers):
    """
    Check if we need to show a section transition message
    before displaying the given question.
    """
    if prev_question_id is None:
        # First question
        section = get_section_for_question(question_id)
        return get_section_transition(section)

    prev_section = get_section_for_question(prev_question_id)
    curr_section = get_section_for_question(question_id)

    if prev_section != curr_section:
        return get_section_transition(curr_section)

    return None


def get_first_question_id():
    """Return the first question id in the flow."""
    if QUESTION_FLOW:
        return QUESTION_FLOW[0]
    return None


def calculate_progress(current_id, user_answers):
    """
    Calculate approximate progress percentage.
    Based on position in the active flow (skipping irrelevant conditionals).
    """
    active_questions = []
    for qid in QUESTION_FLOW:
        q = get_question_by_id(qid)
        if q and should_show_question(q, user_answers):
            active_questions.append(qid)

    if current_id in active_questions:
        idx = active_questions.index(current_id)
        return int((idx / len(active_questions)) * 100)
    return 0
