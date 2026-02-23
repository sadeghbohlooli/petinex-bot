"""Command handlers: /start, /health, /diet, /support, /stats, post_init."""

import logging

from telegram import Update, BotCommand
from telegram.ext import ContextTypes

from config import ADMIN_CHAT_ID
from core.states import MAIN_MENU
from core.session import user_sessions, reset_session
from core.menu import get_main_menu_keyboard, MENU_RESPONSES, BTN_DIET, BTN_SUPPORT
from questions import get_total_all_questions, get_total_base_questions

logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command — show main menu."""
    uid = update.effective_user.id
    reset_session(uid)

    welcome = (
        "🐾 <b>به پتینکس خوش آمدید!</b>\n\n"
        "🏠 از منوی زیر یکی از خدمات رو انتخاب کن:\n\n"
        "🩺 <b>گزارش سلامت پت</b> — ارزیابی هوشمند سلامت حیوانت\n"
        "🥗 <b>دریافت رژیم غذایی</b> — رژیم اختصاصی پت شما\n"
        "👨‍⚕️ <b>دامپزشک آنلاین</b> — مشاوره با متخصص\n"
        "🏥 <b>کلینیک</b> — پیدا کردن کلینیک نزدیک\n"
        "🛒 <b>پت‌شاپ</b> — خرید لوازم و غذا\n"
        "🏠 <b>پانسیون</b> — نگهداری امن پت شما\n"
        "💊 <b>داروخانه</b> — دارو و مکمل\n"
        "✂️ <b>گرومر</b> — اصلاح و زیبایی\n"
        "🎓 <b>مربی</b> — تربیت و اصلاح رفتار\n"
        "📚 <b>آموزش اختصاصی</b> — یادگیری حرفه‌ای\n"
        "📞 <b>پشتیبانی سریع</b> — ارتباط با تیم ما\n\n"
        "👇 یکی رو انتخاب کن!"
    )

    await update.message.reply_text(
        welcome, parse_mode="HTML", reply_markup=get_main_menu_keyboard(),
    )
    return MAIN_MENU


async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shortcut: directly start health assessment via /health command."""
    uid = update.effective_user.id
    from flows.health_flow import start_health_flow  # Lazy import
    return await start_health_flow(uid, update, context)


async def cmd_diet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shortcut: show diet info."""
    await update.message.reply_text(
        MENU_RESPONSES[BTN_DIET],
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(),
    )
    return MAIN_MENU


async def cmd_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Shortcut: show support info."""
    await update.message.reply_text(
        MENU_RESPONSES[BTN_SUPPORT],
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(),
    )
    return MAIN_MENU


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin-only stats command."""
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ فقط ادمین دسترسی داره.")
        return
    active = len(user_sessions)
    await update.message.reply_text(
        f"📊 <b>آمار بات</b>\n{'─' * 25}\n"
        f"👥 Session‌های فعال: {active}\n"
        f"📋 سؤالات کل: {get_total_all_questions()}\n"
        f"📋 سؤالات پایه: {get_total_base_questions()}",
        parse_mode="HTML",
    )


async def post_init(application):
    """Set bot commands so the ☰ menu button appears in Telegram."""
    commands = [
        BotCommand("start", "🐾 شروع ربات"),
        BotCommand("health", "🩺 گزارش سلامت پت"),
        BotCommand("support", "📞 پشتیبانی سریع"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("✅ Bot menu commands set successfully!")
