from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from core.session import ensure_user_session, reset_session
from core.states import MAIN_MENU

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

# ─── پاسخ‌های منو ───
MENU_RESPONSES = {
    BTN_DIET: (
        "🥗 <b>دریافت رژیم غذایی</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 رژیم غذایی اختصاصی متناسب با نژاد، سن و وضعیت سلامت پت شما.\n\n"
        "🔔 داریم با متخصصین تغذیه دامپزشکی روش کار می‌کنیم!"
    ),
    BTN_VET_ONLINE: (
        "👨‍⚕️ <b>دامپزشک آنلاین</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 با دامپزشک‌های متخصص به‌صورت آنلاین مشاوره بگیر.\n\n"
        "🔔 برای اطلاع از زمان راه‌اندازی، همین‌جا باش!"
    ),
    BTN_CLINIC: (
        "🏥 <b>کلینیک</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 کلینیک‌های معتبر دامپزشکی نزدیک شما.\n\n"
        "🔔 منتظر باش، داریم روش کار می‌کنیم!"
    ),
    BTN_PET_SHOP: (
        "🛒 <b>پت‌شاپ</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 خرید غذا، لوازم و اکسسوری حیوانات خانگی.\n\n"
        "🔔 به‌زودی با بهترین محصولات برمی‌گردیم!"
    ),
    BTN_BOARDING: (
        "🏠 <b>پانسیون</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 پانسیون‌های مطمئن برای نگهداری پت شما.\n\n"
        "🔔 این قابلیت در حال توسعه‌ست!"
    ),
    BTN_PHARMACY: (
        "💊 <b>داروخانه</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 دسترسی به داروهای دامپزشکی و مکمل‌ها.\n\n"
        "🔔 به‌زودی فعال میشه!"
    ),
    BTN_GROOMER: (
        "✂️ <b>گرومر و اصلاح</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 رزرو آنلاین گرومر برای اصلاح و حمام پت.\n\n"
        "🔔 یکم دیگه صبر کن!"
    ),
    BTN_TRAINER: (
        "🎓 <b>مربی (رفتاری · تربیتی)</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 آموزش رفتاری و تربیتی با مربی‌های حرفه‌ای.\n\n"
        "🔔 داریم بهترین مربی‌ها رو جمع می‌کنیم!"
    ),
    BTN_EDUCATION: (
        "📚 <b>آموزش اختصاصی</b>\n\n"
        "🔜 این سرویس به‌زودی فعال می‌شه!\n\n"
        "📌 دوره‌های آموزشی تخصصی نگهداری حیوانات خانگی.\n\n"
        "🔔 محتوای آموزشی در حال آماده‌سازیه!"
    ),
    BTN_SUPPORT: (
        "📞 <b>پشتیبانی سریع</b>\n\n"
        "💬 برای ارتباط با تیم پشتیبانی پتینکس:\n\n"
        "📩 ایمیل: support@petinex.ir\n"
        "📱 تلگرام: @PetinexSupport\n\n"
        "⏰ پاسخگویی: شنبه تا پنجشنبه ۹ تا ۲۱"
    ),
}

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
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
    await ensure_user_session(update, context)
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    if user_text == BTN_HEALTH_REPORT:
        reset_session(uid)
        from flows.health_flow import start_health_flow
        return await start_health_flow(uid, context)

    if user_text in MENU_RESPONSES:
        await update.message.reply_text(
            MENU_RESPONSES[user_text],
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

    await update.message.reply_text(
        "🤔 متوجه نشدم! لطفاً از دکمه‌های منو استفاده کن 👇",
        reply_markup=get_main_menu_keyboard()
    )
    return MAIN_MENU
