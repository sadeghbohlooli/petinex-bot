REPORT_PROMPT_TEMPLATE = """
══════════════════════════════════════════════
           🐾 PETINEX ASSESSMENT DATA
══════════════════════════════════════════════

📋 دستورالعمل برای هوش مصنوعی:

تو یک دامپزشک تحلیل‌گر داده هستی. بر اساس داده‌های زیر، یک گزارش سلامت شخصی‌سازی‌شده به زبان فارسی بنویس.

قوانین الزامی:
1. گزارش باید کاملاً به زبان فارسی باشد
2. لحن: صمیمی ولی حرفه‌ای
3. از ایموجی استفاده کن ولی زیاده‌روی نکن
4. هر ادعایی باید بر اساس داده‌های ورودی باشد
5. در انتها حتماً disclaimer بنویس

══════════════════════════════════════════════
                 📊 داده‌های ورودی
══════════════════════════════════════════════

─── بخش ۱: پروفایل بیولوژیک ───
• نوع حیوان: {pet_type}
• نژاد: {breed}
• سن (ماه): {age_months}
• جنسیت: {sex}
• وضعیت عقیم‌سازی: {neutered}

─── بخش ۲: تغذیه واقعی ───
• نوع غذای اصلی: {food_type}
• تعداد وعده در روز: {meals_per_day}
• مدت زمان خوردن غذا: {eating_duration_minutes}
• تعداد تنقلات روزانه: {treats_per_day}
• غذای سفره: {table_scraps}

─── بخش ۳: وضعیت بدنی (BCS Lite) ───
• وزن (کیلوگرم): {weight_kg}
• حس کردن دنده‌ها: {ribs_feel}
• شکل کمر از بالا: {waist_shape}

─── بخش ۴: فعالیت و سبک زندگی ───
• پیاده‌روی/بازی روزانه: {daily_walk_minutes}
• محل زندگی: {living_space}
• ساعات استراحت روزانه: {rest_hours}

─── بخش ۵: سیگنال‌های بالینی ───
• قوام مدفوع: {stool_consistency}
• تغییر آب خوردن: {water_intake}

─── بخش ۶: رفتار و استرس ───
• تغییر انرژی: {energy_change}
• علائم استرسی: {stress_signs}

══════════════════════════════════════════════
           جداول مرجع امتیازدهی
══════════════════════════════════════════════

جدول BCS:
very_visible + clear_waist = BCS 1-3 (لاغر)
easily_felt + clear_waist = BCS 4-5 (ایده‌آل)
easily_felt + slight_waist = BCS 5-6 (نرمال+)
hard_to_feel + slight_waist = BCS 6-7 (اضافه‌وزن)
hard_to_feel + no_waist = BCS 7-8 (چاق)
not_felt + no_waist = BCS 8-9 (چاق مفرط)

سیگنال‌های هشدار:
water_intake much_increased = مراجعه فوری دامپزشک
energy_change much_decreased = مراجعه فوری دامپزشک
stool diarrhea = مراجعه به دامپزشک
stress_signs 3+ مورد = بررسی استرس محیطی

══════════════════════════════════════════════
            ساختار الزامی گزارش
══════════════════════════════════════════════

۱. 🎯 امتیاز کلی Petinex (از ۱۰۰)
۲. ⚡ تحلیل سطح انرژی
۳. 📏 وضعیت بدنی (BCS)
۴. 🍽️ تحلیل تغذیه
۵. 🏃 تحلیل سبک زندگی
۶. 🚨 رادار ریسک
۷. 📋 برنامه عملی ۳۰ روزه
۸. 💬 نکته پایانی + Disclaimer
"""

TRANSLATIONS = {
    "dog": "سگ 🐕", "cat": "گربه 🐈",
    "male": "نر ♂️", "female": "ماده ♀️",
    "yes": "بله ✅", "no": "خیر ❌", "unknown": "نامشخص 🤷",
    "dry": "خشک (کیبل) 🥫", "wet": "کنسرو/پوچ 🥘",
    "homemade": "خونگی/پخته 🍖", "raw": "خام (BARF) 🥩",
    "mixed": "ترکیبی 🔀",
    "1": "۱ وعده", "2": "۲ وعده", "3": "۳ وعده",
    "4plus": "۴ وعده یا بیشتر", "free": "Free-feeding 🍽️",
    "lt2": "کمتر از ۲ دقیقه ⚡", "2to10": "۲ تا ۱۰ دقیقه 🕐",
    "10to30": "۱۰ تا ۳۰ دقیقه 🕑", "gt30": "بیشتر از ۳۰ دقیقه 🐌",
    "0": "هیچ 🚫", "1to2": "۱-۲ عدد", "3to5": "۳-۵ عدد",
    "6plus": "۶+ عدد ⚠️",
    "never": "هرگز 🚫", "sometimes": "گاهی 🔸",
    "often": "اغلب 🔶", "always": "همیشه 🔴",
    "very_visible": "خیلی واضح و برجسته 🦴",
    "easily_felt": "با فشار کم حس می‌شوند ✅",
    "hard_to_feel": "نیاز به فشار 🔶",
    "not_felt": "اصلاً حس نمی‌شوند ❌",
    "clear_waist": "گودی واضح ⌛",
    "slight_waist": "تقریباً صاف ➖",
    "no_waist": "بیضی/گرد 🫃",
    "lt15": "کمتر از ۱۵ دقیقه 🚶",
    "15to30": "۱۵ تا ۳۰ دقیقه 🏃",
    "30to60": "۳۰ تا ۶۰ دقیقه 🏃‍♂️",
    "gt60": "بیشتر از ۶۰ دقیقه 🏃‍♂️💨",
    "indoor_apartment": "آپارتمان 🏠",
    "indoor_house": "خانه ویلایی 🏡",
    "with_outdoor": "دسترسی به حیاط 🌳",
    "mostly_outdoor": "بیشتر بیرون 🌲",
    "lt10": "کمتر از ۱۰ ساعت 😴",
    "10to14": "۱۰-۱۴ ساعت 💤",
    "14to18": "۱۴-۱۸ ساعت 😪",
    "gt18": "بیشتر از ۱۸ ساعت 🛌",
    "normal": "فرم‌دار ✅", "soft": "شل 💧",
    "diarrhea": "اسهال 🔴", "hard": "سفت/یبوست ⚫",
    "variable": "متغیر 🔀",
    "decreased": "کمتر شده ➖", "same": "بدون تغییر ✅",
    "increased": "بیشتر شده ➕",
    "much_increased": "خیلی بیشتر شده 📈⚠️",
    "much_decreased": "خیلی کمتر شده 📉⚠️",
    "none": "هیچکدام 🚫",
    "excessive_licking": "لیسیدن زیاد 👅",
    "chewing": "جویدن پنجه/دم 🦷",
    "vocalization": "پارس/میو بی‌دلیل 🐕",
    "hiding": "پنهان شدن 🙈",
    "trembling": "لرزش/بی‌قراری 😰",
    "inappropriate_elimination": "دستشویی نامناسب 🚽",
}


def translate(value):
    if isinstance(value, list):
        return ", ".join([TRANSLATIONS.get(v, v) for v in value])
    return TRANSLATIONS.get(str(value), str(value))


def generate_prompt(user_data: dict) -> str:
    return REPORT_PROMPT_TEMPLATE.format(
        pet_type=translate(user_data.get("pet_type", "نامشخص")),
        breed=user_data.get("breed", "نامشخص"),
        age_months=user_data.get("age_months", "نامشخص"),
        sex=translate(user_data.get("sex", "نامشخص")),
        neutered=translate(user_data.get("neutered", "نامشخص")),
        food_type=translate(user_data.get("food_type", "نامشخص")),
        meals_per_day=translate(user_data.get("meals_per_day", "نامشخص")),
        eating_duration_minutes=translate(user_data.get("eating_duration_minutes", "نامشخص")),
        treats_per_day=translate(user_data.get("treats_per_day", "نامشخص")),
        table_scraps=translate(user_data.get("table_scraps", "نامشخص")),
        weight_kg=user_data.get("weight_kg", "نامشخص"),
        ribs_feel=translate(user_data.get("ribs_feel", "نامشخص")),
        waist_shape=translate(user_data.get("waist_shape", "نامشخص")),
        daily_walk_minutes=translate(user_data.get("daily_walk_minutes", "نامشخص")),
        living_space=translate(user_data.get("living_space", "نامشخص")),
        rest_hours=translate(user_data.get("rest_hours", "نامشخص")),
        stool_consistency=translate(user_data.get("stool_consistency", "نامشخص")),
        water_intake=translate(user_data.get("water_intake", "نامشخص")),
        energy_change=translate(user_data.get("energy_change", "نامشخص")),
        stress_signs=translate(user_data.get("stress_signs", ["نامشخص"])),
    )
