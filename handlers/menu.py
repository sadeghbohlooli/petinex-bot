"""
handlers/menu.py
────────────────
هندلر منوی اصلی + لغو ارزیابی.
کپی دقیق از main.py اصلی — بدون هیچ تغییری در منطق.
"""

from telegram import Update
from telegram.ext import ContextTypes

from questions import get_first_question_id

from core.sessions import get_session, reset_session
from core.menu import BTN_HEALTH_REPORT, MENU_RESPONSES
from core.keyboards import get_main_menu_keyboard

# Conversation states (must match main.py)
MAIN_MENU = 0
ANSWERING = 1
MULTI_SELECT = 2
OTHER_TEXT = 3


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle button presses in the main menu."""
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    # Health Report → Start assessment
    if user_text == BTN_HEALTH_REPORT:
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

    # Other menu items → Show info
    if user_text in MENU_RESPONSES:
        await update.message.reply_text(
            MENU_RESPONSES[user_text],
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard(),
        )
        return MAIN_MENU

    # Unknown text
    await update.message.reply_text(
        "🤔 متوجه نشدم! لطفاً از دکمه‌های منو استفاده کن 👇",
        reply_markup=get_main_menu_keyboard(),
    )
    return MAIN_MENU


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the assessment and return to main menu."""
    uid = update.effective_user.id
    reset_session(uid)

    await update.message.reply_text(
        "❌ ارزیابی لغو شد.\n\n🏠 برگشتی به منوی اصلی 👇",
        reply_markup=get_main_menu_keyboard(),
    )
    return MAIN_MENU
