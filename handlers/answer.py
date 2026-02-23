"""
handlers/answer.py
──────────────────
هندلرهای پاسخ‌دهی (تک‌انتخابی، عددی، متنی، چندانتخابی).
کپی دقیق از main.py اصلی — بدون هیچ تغییری در منطق.
"""

import logging

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from questions import (
    get_question_by_id,
    get_options_for_question,
)

from core.sessions import get_session
from core.keyboards import (
    find_option_value,
    build_multi_reply_keyboard,
)
from core.progress import get_progress_text

# Conversation states (must match main.py)
MAIN_MENU = 0
ANSWERING = 1
MULTI_SELECT = 2
OTHER_TEXT = 3

logger = logging.getLogger(__name__)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle single-choice and text/number input answers."""
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    # Cancel check
    if user_text == "❌ انصراف و بازگشت":
        from handlers.menu import handle_cancel
        return await handle_cancel(update, context)

    session = get_session(uid)
    qid = session.get("current_question_id")
    if qid is None:
        return MAIN_MENU

    question = get_question_by_id(qid)
    if not question:
        logger.error(f"Question {qid} not found in handle_answer")
        return MAIN_MENU

    answers = session["answers"]
    q_type = question["type"]
    variable = question["variable"]

    # ── Waiting for "other" free text ──
    if session.get("waiting_for_other_text"):
        other_var = session.get("other_text_variable", variable + "_other")
        answers[other_var] = user_text
        session["waiting_for_other_text"] = False
        session["other_text_variable"] = None
        await update.message.reply_text(f"✅ ثبت شد: {user_text}")
        from flows.assessment import advance
        return await advance(uid, context)

    # ── TEXT INPUT ──
    if q_type == "text_input":
        # Check if there are button options too (e.g., Q33 "no concern" button)
        if question.get("options"):
            value = find_option_value(question, user_text, answers)
            if value:
                answers[variable] = value
                from flows.assessment import advance
                return await advance(uid, context)

        # Otherwise treat as free text
        answers[variable] = user_text
        from flows.assessment import advance
        return await advance(uid, context)

    # ── NUMBER INPUT ──
    elif q_type == "number_input":
        cleaned = user_text.replace(",", ".").replace("٫", ".").replace("،", ".")
        # Remove Persian/Arabic numerals → convert to Western
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        arabic_digits = "٠١٢٣٤٥٦٧٨٩"
        for i, (p, a) in enumerate(zip(persian_digits, arabic_digits)):
            cleaned = cleaned.replace(p, str(i)).replace(a, str(i))

        try:
            num_val = float(cleaned)
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً یک عدد معتبر وارد کن.\nمثلاً: 4.5 یا ۸"
            )
            return ANSWERING

        # Validate range
        num_range = question.get("number_range")
        if num_range:
            if num_val < num_range["min"] or num_val > num_range["max"]:
                await update.message.reply_text(
                    f"❌ عدد باید بین {num_range['min']} و {num_range['max']} باشه.\n"
                    f"لطفاً دوباره وارد کن:"
                )
                return ANSWERING

        answers[variable] = num_val
        from flows.assessment import advance
        return await advance(uid, context)

    # ── INLINE BUTTON (single select) ──
    elif q_type == "inline_button":
        value = find_option_value(question, user_text, answers)

        if value is None:
            await update.message.reply_text(
                "⚠️ لطفاً یکی از گزینه‌های موجود رو انتخاب کن!"
            )
            return ANSWERING

        # Check if this is "_other" option (needs follow-up text)
        if value == "_other" and question.get("has_other_text"):
            answers[variable] = "_other"
            session["waiting_for_other_text"] = True
            session["other_text_variable"] = variable + "_detail"

            await update.message.reply_text(
                "✏️ لطفاً بنویس:",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("❌ انصراف و بازگشت")]],
                    resize_keyboard=True,
                ),
            )
            return ANSWERING

        answers[variable] = value
        from flows.assessment import advance
        return await advance(uid, context)

    return ANSWERING


async def handle_multi_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle multi-select question interactions."""
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    # Cancel check
    if user_text == "❌ انصراف و بازگشت":
        from handlers.menu import handle_cancel
        return await handle_cancel(update, context)

    session = get_session(uid)
    qid = session.get("current_question_id")
    question = get_question_by_id(qid)

    if not question:
        return MAIN_MENU

    answers = session["answers"]
    options = get_options_for_question(question, answers)
    confirm_text = question.get("confirm_button", "✅ تأیید و ادامه")

    # ── Confirm button pressed ──
    if user_text == confirm_text:
        final = session["multi_select_temp"] if session["multi_select_temp"] else ["none"]
        answers[question["variable"]] = final
        session["multi_select_temp"] = []

        if final != ["none"]:
            selected_texts = []
            for v in final:
                if options:
                    for opt in options:
                        if opt["value"] == v:
                            selected_texts.append(opt["text"])
            if selected_texts:
                await update.message.reply_text(
                    "✅ انتخاب‌های شما:\n" + "\n".join(f"  • {t}" for t in selected_texts)
                )

        # Check if "_other" was selected and needs text
        if "_other" in final and question.get("has_other_text"):
            session["multi_select_temp"] = []  # Clear
            session["waiting_for_other_text"] = True
            session["other_text_variable"] = question["variable"] + "_detail"

            await update.message.reply_text(
                "✏️ لطفاً جزئیات رو بنویس:",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("❌ انصراف و بازگشت")]],
                    resize_keyboard=True,
                ),
            )
            return ANSWERING

        from flows.assessment import advance
        return await advance(uid, context)

    # ── Toggle option ──
    clean_text = user_text.replace(" ✅", "").strip()
    value = None
    if options:
        for opt in options:
            if opt["text"] == clean_text:
                value = opt["value"]
                break

    if value is None:
        await update.message.reply_text(
            "⚠️ لطفاً یکی از گزینه‌ها رو انتخاب کن یا دکمه تأیید رو بزن!"
        )
        return MULTI_SELECT

    temp = session["multi_select_temp"]

    # "none" / "all_normal" / "nothing" → clear others
    exclusive_values = {"none", "all_normal", "nothing", "healthy", "dont_remember"}
    if value in exclusive_values:
        session["multi_select_temp"] = [value]
        await update.message.reply_text(f"✅ انتخاب شد: {clean_text}")
    else:
        # Remove exclusive values if present
        for ev in exclusive_values:
            if ev in temp:
                temp.remove(ev)

        if value in temp:
            temp.remove(value)
            await update.message.reply_text(f"❌ حذف شد: {clean_text}")
        else:
            temp.append(value)
            await update.message.reply_text(f"✅ اضافه شد: {clean_text}")

    # Re-send question with updated keyboard
    progress = get_progress_text(qid, answers)
    q_text = question["text"]
    text = f"{progress}\n\n{q_text}"
    if question.get("micro_copy"):
        text += f"\n\n{question['micro_copy']}"

    kb = build_multi_reply_keyboard(question, session["multi_select_temp"], answers)
    await update.message.reply_text(text=text, reply_markup=kb, parse_mode="HTML")
    return MULTI_SELECT
