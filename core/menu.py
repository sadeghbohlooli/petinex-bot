# core/menu.py
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from core.session import reset_session
from core.states import MAIN_MENU

# دکمه‌های منوی اصلی
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

# پاسخ‌های موقت برای دکمه‌هایی که هنوز فعال نیستند
MENU_RESPONSES = {
    BTN_DIET: "🥗 <b>دریافت رژیم غذایی</b>\n\n🔜 به‌زودی...",
    BTN_VET_ONLINE: "👨‍⚕️ <b>دامپزشک آنلاین</b>\n\n🔜 به‌زودی...",
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

def get_main_menu_keyboard():
    """کیبورد منوی اصلی را می‌سازد."""
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

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """مدیریت کلیک روی دکمه‌های منوی اصلی."""
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    # اگر دکمه گزارش سلامت کلیک شد
    if user_text == BTN_HEALTH_REPORT:
        reset_session(uid)
        # ایمپورت درون تابع برای جلوگیری از circular import
        from flows.health_flow import start_health_flow
        return await start_health_flow(uid, context)

    # اگر دکمه‌های دیگر (که فعلاً غیرفعال هستند) کلیک شدند
    if user_text in MENU_RESPONSES:
        await update.message.reply_text(
            MENU_RESPONSES[user_text],
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

    # اگر کاربر متن نامربوط فرستاد
    await update.message.reply_text(
        "🤔 متوجه نشدم! از دکمه‌های منو استفاده کن.",
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU
