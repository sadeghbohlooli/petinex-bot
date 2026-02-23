"""
فلوی گزارش سلامت — تمام منطق مربوط به ارزیابی سلامت.
شامل: شروع فلو، ارسال سؤال، دریافت جواب، اتمام ارزیابی
"""

import logging
from datetime import datetime

from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler, ContextTypes

from config import ADMIN_CHAT_ID
from core.states import MAIN_MENU, ANSWERING, MULTI_SELECT
from core.session import get_session, reset_session
from core.keyboards import build_reply_keyboard, build_multi_reply_keyboard
from core.progress import get_progress_text
from questions import (
    QUESTION_FLOW,
    COMPLETION_MESSAGE,
    get_question_by_id,
    get_options_for_question,
    should_show_question,
    get_next_question_id,
    should_show_section_transition,
    get_first_question_id,
)
from prompt_template import generate_prompt

logger = logging.getLogger(__name__)


# ============================================================
# START HEALTH FLOW
# ============================================================

async def start_health_flow(uid: int, update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع فلوی ارزیابی سلامت — فراخوانی از cmd_health یا handle_main_menu."""
    reset_session(uid)
    session = get_session(uid)

    session["active_flow"] = "health"
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
    return await send_question(uid, context)


# ============================================================
# SEND QUESTION TO USER
# ============================================================

async def send_question(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send the current question to the user, handling all types."""
    session = get_session(uid)
    qid = session["current_question_id"]

    if qid is None:
        return ConversationHandler.END

    question = get_question_by_id(qid)
    if not question:
        logger.error(f"Question ID {qid} not found!")
        return ConversationHandler.END

    answers = session["answers"]

    # ── Check if we need a section transition message ──
    transition_msg = should_show_section_transition(
        qid, session.get("prev_question_id"), answers
    )
    if transition_msg:
        await context.bot.send_message(
            chat_id=uid, text=transition_msg, parse_mode="HTML"
        )

    # ── Build question text ──
    progress = get_progress_text(qid, answers)
    pet_name = answers.get("pet_name", "پتت")

    q_text = question["text"].replace("{pet_name}", pet_name)

    text = f"{progress}\n\n{q_text}"
    if question.get("micro_copy"):
        text += f"\n\n{question['micro_copy']}"

    q_type = question["type"]

    # ── TEXT INPUT ──
    if q_type == "text_input":
        if question.get("options"):
            kb = build_reply_keyboard(question, answers)
            placeholder = question.get("placeholder", "پاسخ خود را بنویسید...")
        else:
            kb = ReplyKeyboardMarkup(
                [[KeyboardButton("❌ انصراف و بازگشت")]],
                resize_keyboard=True,
            )
            placeholder = question.get("placeholder", "")

        if placeholder:
            text += f"\n\n💡 {placeholder}"

        await context.bot.send_message(
            chat_id=uid, text=text, parse_mode="HTML", reply_markup=kb,
        )
        return ANSWERING

    # ── NUMBER INPUT ──
    elif q_type == "number_input":
        kb = ReplyKeyboardMarkup(
            [[KeyboardButton("❌ انصراف و بازگشت")]],
            resize_keyboard=True,
        )
        placeholder = question.get("placeholder", "")
        if placeholder:
            text += f"\n\n💡 {placeholder}"

        num_range = question.get("number_range")
        if num_range:
            text += f"\n(محدوده مجاز: {num_range['min']} تا {num_range['max']})"

        await context.bot.send_message(
            chat_id=uid, text=text, parse_mode="HTML", reply_markup=kb,
        )
        return ANSWERING

    # ── MULTI SELECT ──
    elif q_type == "multi_select":
        session["multi_select_temp"] = []
        kb = build_multi_reply_keyboard(question, [], answers)
        await context.bot.send_message(
            chat_id=uid, text=text, parse_mode="HTML", reply_markup=kb,
        )
        return MULTI_SELECT

    # ── INLINE BUTTON (single select) ──
    else:
        kb = build_reply_keyboard(question, answers)
        await context.bot.send_message(
            chat_id=uid, text=text, parse_mode="HTML", reply_markup=kb,
        )
        return ANSWERING


# ============================================================
# ADVANCE TO NEXT QUESTION
# ============================================================

async def advance(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Move to the next applicable question or finish the assessment."""
    session = get_session(uid)
    current_id = session["current_question_id"]
    answers = session["answers"]

    next_id = get_next_question_id(current_id, answers)

    if next_id is None:
        await finish_assessment(uid, context)
        return MAIN_MENU
    else:
        session["prev_question_id"] = current_id
        session["current_question_id"] = next_id
        return await send_question(uid, context)


# ============================================================
# FINISH ASSESSMENT
# ============================================================

async def finish_assessment(uid: int, context: ContextTypes.DEFAULT_TYPE):
    """Complete the assessment, send data to admin, notify user."""
    from core.menu import get_main_menu_keyboard  # Lazy import

    session = get_session(uid)

    try:
        chat = await context.bot.get_chat(uid)
        full_name = chat.full_name or "ناشناس"
        username = f"@{chat.username}" if chat.username else "ندارد"
    except Exception:
        full_name = "خطا"
        username = "خطا"

    prompt = generate_prompt(session["answers"])
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = (
        f"🔔 ارزیابی جدید دریافت شد!\n"
        f"{'─' * 30}\n"
        f"👤 نام: {full_name}\n"
        f"🆔 یوزرنیم: {username}\n"
        f"🔢 Chat ID: {uid}\n"
        f"⏰ زمان: {now}\n"
        f"📊 تعداد سؤالات پاسخ داده: {len(session['answers'])}\n"
        f"{'─' * 30}\n"
        f"💡 برای ارسال PDF، روی این پیام Reply کن و فایل رو بفرست.\n"
        f"{'─' * 30}\n"
    )

    full_msg = header + "\n" + prompt
    chunks = [full_msg[i: i + 4000] for i in range(0, len(full_msg), 4000)]
    for i, chunk in enumerate(chunks):
        prefix = f"📄 بخش {i + 1}/{len(chunks)}:\n\n" if len(chunks) > 1 else ""
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID, text=prefix + chunk
            )
        except Exception as e:
            logger.error(f"Failed to send to admin: {e}")

    await context.bot.send_message(
        chat_id=uid,
        text=COMPLETION_MESSAGE,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(),
    )

    reset_session(uid)
    logger.info(f"Assessment completed for user {uid} ({full_name})")
