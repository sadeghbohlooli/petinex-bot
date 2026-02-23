"""
handlers/commands.py
────────────────────
هندلرهای command ربات (/start, /health, /diet, /support, /stats).
کپی دقیق از main.py اصلی — بدون هیچ تغییری در منطق.
"""

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_CHAT_ID
from questions import (
    get_first_question_id,
    get_total_all_questions,
    get_total_base_questions,
)

from core.sessions import get_session, reset_session, user_sessions
from core.menu import BTN_DIET, BTN_SUPPORT, MENU_RESPONSES
from core.keyboards import get_main_menu_keyboard

# Conversation states (must match main.py)
MAIN_MENU = 0
ANSWERING = 1
MULTI_SELECT = 2
OTHER_TEXT = 3


# ============================================================
# send_question will be injected from flows module later.
# For now, we import it at call-time to avoid circular imports.
# ============================================================


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
    reset_session(uid)
    session = get_session(uid)

    first_id = get_first_question_id()
    session["current_question_id"] = first_id
    session["prev_question_id"] = None

    await update.message.reply_text(
        "🩺 <b>شروع ارزیابی سلامت پت</b>\n\n"
        "📝 الان چند تا سؤال ازت می‌پرسم.\n"
        "⏱ حدود ۵ تا ۱۰ دقیقه وقتت رو می‌گیره.\n\n"
        "❌ هر لحظه می‌تونی «انصراف و بازگشت» رو بزنی.\n\n"
        "بزن بریم! 👇",
        parse_mode="HTML",
    )

    # Import here to avoid circular imports
    from flows.assessment import send_question
    return await send_question(uid, context)


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
