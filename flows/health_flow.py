import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from core.session import get_session, reset_session
from core.keyboards import (
    build_option_keyboard,
    build_multi_select_keyboard,
    find_option_value,
    cancel_only_keyboard,
)
from core.menu import get_main_menu_keyboard
from core.states import ANSWERING, MULTI_SELECT, MAIN_MENU
from questions.health_questions import (
    get_question_by_id,
    get_options_for_question,
    should_show_question,
    get_next_question_id,
    get_first_question_id,
    calculate_progress,
    should_show_section_transition,
)
from prompts.health_prompt import generate_health_prompt
from config import ADMIN_CHAT_ID

logger = logging.getLogger(__name__)

async def ensure_health_session(uid: int) -> dict:
    session = get_session(uid)
    if session.get("active_flow") != "health":
        reset_session(uid)
        session = get_session(uid)
        session["active_flow"] = "health"
        session["current_question_id"] = get_first_question_id()
        session["prev_question_id"] = None
        session["answers"] = {}
        session["multi_select_temp"] = []
        session["waiting_for_other_text"] = False
        session["other_text_variable"] = None
        logger.info(f"New health session for {uid}, first question: {session['current_question_id']}")
    elif session.get("current_question_id") is None:
        session["current_question_id"] = get_first_question_id()
        logger.info(f"Session had no current question, reset to first: {session['current_question_id']}")
    return session

async def start_health_flow(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        session = await ensure_health_session(uid)
        first_id = session["current_question_id"]
        if first_id is None:
            await context.bot.send_message(chat_id=uid, text="❌ خطای سیستمی: اولین سوال یافت نشد!")
            return MAIN_MENU

        await context.bot.send_message(
            chat_id=uid,
            text="🩺 <b>شروع ارزیابی سلامت پت</b>\n\n📝 الان چند تا سؤال می‌پرسم.\n⏱ حدود ۵ تا ۱۰ دقیقه وقتت رو می‌گیره.\n\n❌ هر لحظه می‌تونی «انصراف و بازگشت» رو بزنی.\n\nبزن بریم! 👇",
            parse_mode="HTML",
        )
        return await send_question(uid, context)
    except Exception as e:
        await context.bot.send_message(chat_id=uid, text=f"❌ خطا در شروع ارزیابی: {str(e)}")
        return MAIN_MENU

async def send_question(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        session = await ensure_health_session(uid)
        qid = session.get("current_question_id")
        if qid is None:
            await context.bot.send_message(chat_id=uid, text="❌ خطا: شناسه سؤال نامشخص! لطفاً دوباره از منوی اصلی شروع کنید.")
            reset_session(uid)
            return MAIN_MENU

        question = get_question_by_id(qid)
        if not question:
            await context.bot.send_message(chat_id=uid, text=f"❌ خطا: سؤال {qid} یافت نشد!")
            reset_session(uid)
            return MAIN_MENU

        answers = session.get("answers", {})
        transition_msg = should_show_section_transition(qid, session.get("prev_question_id"), answers)
        if transition_msg:
            await context.bot.send_message(chat_id=uid, text=transition_msg, parse_mode="HTML")

        progress = calculate_progress(qid, answers)
        pet_name = answers.get("pet_name", "پتت")
        q_text = question["text"].replace("{pet_name}", pet_name)
        text = f"{progress}\n\n{q_text}"
        if question.get("micro_copy"):
            text += f"\n\n{question['micro_copy']}"

        q_type = question["type"]
        options = get_options_for_question(question, answers)

        if q_type == "text_input":
            if options:
                kb = build_option_keyboard(options)
            else:
                kb = cancel_only_keyboard()
            if question.get("placeholder"):
                text += f"\n\n💡 {question['placeholder']}"
            await context.bot.send_message(chat_id=uid, text=text, parse_mode="HTML", reply_markup=kb)
            return ANSWERING

        elif q_type == "number_input":
            kb = cancel_only_keyboard()
            if question.get("placeholder"):
                text += f"\n\n💡 {question['placeholder']}"
            num_range = question.get("number_range")
            if num_range:
                text += f"\n(محدوده مجاز: {num_range['min']} تا {num_range['max']})"
            await context.bot.send_message(chat_id=uid, text=text, parse_mode="HTML", reply_markup=kb)
            return ANSWERING

        elif q_type == "multi_select":
            session["multi_select_temp"] = []
            kb = build_multi_select_keyboard(options, [], question.get("confirm_button", "✅ تأیید و ادامه"))
            await context.bot.send_message(chat_id=uid, text=text, parse_mode="HTML", reply_markup=kb)
            return MULTI_SELECT

        else:  # inline_button
            kb = build_option_keyboard(options)
            await context.bot.send_message(chat_id=uid, text=text, parse_mode="HTML", reply_markup=kb)
            return ANSWERING

    except Exception as e:
        await context.bot.send_message(chat_id=uid, text=f"❌ خطای غیرمنتظره در ارسال سوال: {str(e)}")
        reset_session(uid)
        return MAIN_MENU

async def handle_health_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    if user_text == "❌ انصراف و بازگشت":
        return await cancel_health(update, context)

    try:
        session = await ensure_health_session(uid)
        qid = session.get("current_question_id")
        if qid is None:
            await update.message.reply_text("❌ خطا: اطلاعات جلسه از بین رفته. لطفاً دوباره از منوی اصلی شروع کنید.")
            reset_session(uid)
            return MAIN_MENU

        question = get_question_by_id(qid)
        if not question:
            await update.message.reply_text(f"❌ خطا: سؤال {qid} یافت نشد!")
            reset_session(uid)
            return MAIN_MENU

        answers = session.get("answers", {})
        q_type = question["type"]
        variable = question["variable"]

        if session.get("waiting_for_other_text"):
            other_var = session.get("other_text_variable", variable + "_other")
            answers[other_var] = user_text
            session["waiting_for_other_text"] = False
            session["other_text_variable"] = None
            await update.message.reply_text(f"✅ ثبت شد: {user_text}")
            return await advance(uid, context)

        if q_type == "text_input" and question.get("options"):
            value = find_option_value(question["options"], user_text)
            if value:
                answers[variable] = value
            else:
                answers[variable] = user_text
            await update.message.reply_text(f"✅ پاسخ شما ثبت شد.")
            return await advance(uid, context)

        if q_type == "text_input":
            answers[variable] = user_text
            await update.message.reply_text(f"✅ پاسخ شما ثبت شد.")
            return await advance(uid, context)

        if q_type == "number_input":
            cleaned = user_text.replace(",", ".").replace("٫", ".").replace("،", ".")
            persian_digits = "۰۱۲۳۴۵۶۷۸۹"
            arabic_digits = "٠١٢٣٤٥٦٧٨٩"
            for i, (p, a) in enumerate(zip(persian_digits, arabic_digits)):
                cleaned = cleaned.replace(p, str(i)).replace(a, str(i))
            try:
                num_val = float(cleaned)
            except ValueError:
                await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کن.")
                return ANSWERING
            num_range = question.get("number_range")
            if num_range:
                if num_val < num_range["min"] or num_val > num_range["max"]:
                    await update.message.reply_text(f"❌ عدد باید بین {num_range['min']} و {num_range['max']} باشه.")
                    return ANSWERING
            answers[variable] = num_val
            await update.message.reply_text(f"✅ عدد {num_val} ثبت شد.")
            return await advance(uid, context)

        if q_type == "inline_button":
            options = get_options_for_question(question, answers)
            value = find_option_value(options, user_text)
            if value is None:
                await update.message.reply_text("⚠️ لطفاً یکی از گزینه‌ها رو انتخاب کن.")
                return ANSWERING
            if value == "_other" and question.get("has_other_text"):
                answers[variable] = "_other"
                session["waiting_for_other_text"] = True
                session["other_text_variable"] = variable + "_detail"
                await update.message.reply_text("✏️ لطفاً بنویس:", reply_markup=cancel_only_keyboard())
                return ANSWERING
            answers[variable] = value
            await update.message.reply_text(f"✅ گزینه انتخاب شده ثبت شد.")
            return await advance(uid, context)

        return ANSWERING
    except Exception as e:
        await update.message.reply_text(f"❌ خطای غیرمنتظره: {str(e)}")
        reset_session(uid)
        return MAIN_MENU

async def handle_health_multi_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    if user_text == "❌ انصراف و بازگشت":
        return await cancel_health(update, context)

    try:
        session = await ensure_health_session(uid)
        qid = session.get("current_question_id")
        question = get_question_by_id(qid)
        if not question:
            await update.message.reply_text("❌ خطا: سؤال یافت نشد!")
            reset_session(uid)
            return MAIN_MENU

        answers = session.get("answers", {})
        options = get_options_for_question(question, answers)
        confirm_text = question.get("confirm_button", "✅ تأیید و ادامه")

        if user_text == confirm_text:
            final = session.get("multi_select_temp", []) if session.get("multi_select_temp") else ["none"]
            answers[question["variable"]] = final
            session["multi_select_temp"] = []
            await update.message.reply_text("✅ انتخاب شما ثبت شد.")
            return await advance(uid, context)

        value = find_option_value(options, user_text)
        if value is None:
            await update.message.reply_text("⚠️ لطفاً یکی از گزینه‌ها رو انتخاب کن.")
            return MULTI_SELECT

        temp = session.get("multi_select_temp", [])
        exclusive = {"none", "all_normal", "nothing", "healthy", "dont_remember"}
        if value in exclusive:
            session["multi_select_temp"] = [value]
        else:
            for ev in exclusive:
                if ev in temp:
                    temp.remove(ev)
            if value in temp:
                temp.remove(value)
            else:
                temp.append(value)
            session["multi_select_temp"] = temp

        progress = calculate_progress(qid, answers)
        pet_name = answers.get("pet_name", "پتت")
        q_text = question["text"].replace("{pet_name}", pet_name)
        text = f"{progress}\n\n{q_text}"
        if question.get("micro_copy"):
            text += f"\n\n{question['micro_copy']}"
        kb = build_multi_select_keyboard(options, session["multi_select_temp"], confirm_text)
        await update.message.reply_text(text=text, reply_markup=kb, parse_mode="HTML")
        return MULTI_SELECT
    except Exception as e:
        await update.message.reply_text(f"❌ خطای غیرمنتظره: {str(e)}")
        reset_session(uid)
        return MAIN_MENU

async def advance(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    session = await ensure_health_session(uid)
    current_id = session.get("current_question_id")
    if current_id is None:
        logger.error(f"Advance called with no current_question_id for user {uid}")
        reset_session(uid)
        return MAIN_MENU

    answers = session.get("answers", {})
    next_id = get_next_question_id(current_id, answers)
    logger.info(f"Advance from {current_id} to {next_id} for user {uid}")

    if next_id is None:
        return await finish_health(uid, context)
    else:
        session["prev_question_id"] = current_id
        session["current_question_id"] = next_id
        return await send_question(uid, context)

async def finish_health(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    session = get_session(uid)

    try:
        chat = await context.bot.get_chat(uid)
        full_name = chat.full_name or "ناشناس"
        username = f"@{chat.username}" if chat.username else "ندارد"
    except:
        full_name = "خطا"
        username = "خطا"

    prompt = generate_health_prompt(session.get("answers", {}))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = (
        f"🔔 ارزیابی جدید دریافت شد!\n"
        f"{'─'*30}\n"
        f"👤 نام: {full_name}\n"
        f"🆔 یوزرنیم: {username}\n"
        f"🔢 Chat ID: {uid}\n"
        f"⏰ زمان: {now}\n"
        f"📊 تعداد پاسخ‌ها: {len(session.get('answers', {}))}\n"
        f"{'─'*30}\n"
        f"💡 برای ارسال PDF، روی این پیام Reply کن.\n"
        f"{'─'*30}\n"
    )

    full_msg = header + "\n" + prompt
    for i in range(0, len(full_msg), 4000):
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=full_msg[i:i+4000])

    await context.bot.send_message(
        chat_id=uid,
        text="✅ ممنون! گزارش سلامت پتت داره آماده می‌شه.\n🕐 تا ۲۴ ساعت آینده برات ارسال میشه.",
        reply_markup=get_main_menu_keyboard(),
    )

    reset_session(uid)
    return MAIN_MENU

async def cancel_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.effective_user.id
    reset_session(uid)
    await update.message.reply_text(
        "❌ ارزیابی لغو شد.\n🏠 برگشتی به منوی اصلی 👇",
        reply_markup=get_main_menu_keyboard(),
    )
    return MAIN_MENU
