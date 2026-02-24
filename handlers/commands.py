from telegram import Update, BotCommand
from telegram.ext import ContextTypes
from core.session import ensure_user_session, reset_session, get_all_sessions
from core.menu import get_main_menu_keyboard, MENU_RESPONSES, BTN_DIET, BTN_SUPPORT
from core.states import MAIN_MENU
from flows.health_flow import start_health_flow
from config import ADMIN_CHAT_ID

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # اطمینان از وجود session و لود اطلاعات از دیتابیس
    session = await ensure_user_session(update, context)
    uid = update.effective_user.id

    if session.get("user_id"):
        # کاربر قبلاً عضو شده
        welcome = (
            "🐾 <b>به پتینکس خوش برگشتی!</b>\n\n"
            "🏠 از منوی زیر یکی از خدمات رو انتخاب کن:\n\n"
            "🩺 <b>گزارش سلامت پت</b> — ارزیابی هوشمند سلامت\n"
            "🥗 <b>دریافت رژیم غذایی</b> — رژیم اختصاصی\n"
            "👨‍⚕️ <b>دامپزشک آنلاین</b> — مشاوره با متخصص\n"
            "📞 <b>پشتیبانی سریع</b> — ارتباط با تیم ما\n\n"
            "👇 یکی رو انتخاب کن!"
        )
    else:
        # کاربر جدید
        welcome = (
            "🐾 <b>به پتینکس خوش آمدید!</b>\n\n"
            "🏠 از منوی زیر یکی از خدمات رو انتخاب کن:\n\n"
            "🩺 <b>گزارش سلامت پت</b> — ارزیابی هوشمند سلامت\n"
            "🥗 <b>دریافت رژیم غذایی</b> — رژیم اختصاصی\n"
            "👨‍⚕️ <b>دامپزشک آنلاین</b> — مشاوره با متخصص\n"
            "📞 <b>پشتیبانی سریع</b> — ارتباط با تیم ما\n\n"
            "👇 یکی رو انتخاب کن!"
        )

    await update.message.reply_text(welcome, parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await ensure_user_session(update, context)
    uid = update.effective_user.id
    return await start_health_flow(uid, context)

async def cmd_diet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await ensure_user_session(update, context)
    await update.message.reply_text(MENU_RESPONSES[BTN_DIET], parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def cmd_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await ensure_user_session(update, context)
    await update.message.reply_text(MENU_RESPONSES[BTN_SUPPORT], parse_mode="HTML", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ فقط ادمین.")
        return
    active = len(get_all_sessions())
    await update.message.reply_text(f"📊 آمار بات\n{'─'*25}\n👥 Session‌های فعال: {active}", parse_mode="HTML")

async def post_init(application):
    commands = [
        BotCommand("start", "🐾 شروع ربات"),
        BotCommand("health", "🩺 گزارش سلامت پت"),
        BotCommand("support", "📞 پشتیبانی سریع"),
    ]
    await application.bot.set_my_commands(commands)
