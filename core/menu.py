# core/menu.py
"""منوی اصلی ربات — دکمه‌ها و پاسخ‌های ثابت."""
from telegram import ReplyKeyboardMarkup, KeyboardButton

# ─── دکمه‌ها ───
BTN_HEALTH_REPORT = "🩺 گزارش سلامت پت"
BTN_DIET = "🥗 دریافت رژیم غذایی"
BTN_VET_ONLINE = "👨‍⚕️ دامپزشک (آنلاین)"
BTN_CLINIC = "🏥 کلینیک"
BTN_PET_SHOP = "🛒 پت‌شاپ"
BTN_BOARDING = "🏠 پانسیون"
BTN_PHARMACY = "💊 داروخانه"
BTN_GROOMER = "✂️ گرومر و اصلاح"
BTN_TRAINER = "🎓 مربی (رفتاری · تربیتی)"
BTN_EDUCATION = "📚 آموزش اختصاصی"
BTN_SUPPORT = "📞 پشتیبانی سریع"

# ─── پاسخ‌های منو (برای دکمه‌هایی که هنوز فعال نیستند) ───
MENU_RESPONSES = {
    BTN_DIET: (
        "🥗 <b>دریافت رژیم غذایی</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 رژیم غذایی اختصاصی متناسب با نژاد، سن و وضعیت سلامت پت شما.\n\n"
        "🔔 داریم با متخصصین تغذیه دامپزشکی روش کار می‌کنیم!"
    ),
    BTN_VET_ONLINE: (
        "👨‍⚕️ <b>دامپزشک آنلاین</b>\n\n"
        "🔜 به‌زودی..."
    ),
    BTN_CLINIC: "🏥 <b>کلینیک</b>\n\n🔜 به‌زودی...",
    BTN_PET_SHOP: "🛒 <b>پت‌شاپ</b>\n\n🔜 به‌زودی...",
    BTN_BOARDING: "🏠 <b>پانسیون</b>\n\n🔜 به‌زودی...",
    BTN_PHARMACY: "💊 <b>داروخانه</b>\n\n🔜 به‌زودی...",
    BTN_GROOMER: "✂️ <b>گرومر</b>\n\n🔜 به‌زودی...",
    BTN_TRAINER: "🎓 <b>مربی</b>\n\n🔜 به‌زودی...",
    BTN_EDUCATION: "📚 <b>آموزش اختصاصی</b>\n\n🔜 به‌زودی...",
    BTN_SUPPORT: (
        "📞 <b>پشتیبانی سریع</b>\n\n"
        "💬 ایمیل: support@petinex.ir\n"
        "📱 تلگرام: @PetinexSupport\n"
        "⏰ پاسخگویی: شنبه تا پنجشنبه ۹ تا ۲۱"
    ),
}

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """کیبورد منوی اصلی."""
    keyboard = [
        [KeyboardButton(BTN_HEALTH_REPORT)],
        [KeyboardButton(BTN_DIET), KeyboardButton(BTN_VET_ONLINE)],
        [KeyboardButton(BTN_CLINIC), KeyboardButton(BTN_PET_SHOP)],
        [KeyboardButton(BTN_BOARDING), KeyboardButton(BTN_PHARMACY)],
        [KeyboardButton(BTN_GROOMER), KeyboardButton(BTN_TRAINER)],
        [KeyboardButton(BTN_EDUCATION)],
        [KeyboardButton(BTN_SUPPORT)],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
