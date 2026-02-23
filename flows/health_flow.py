# flows/health_flow.py
"""فلوی گزارش سلامت — تمام منطق مربوط به ارزیابی سلامت."""
import logging
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

async def start_health_flow(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    """شروع فلوی سلامت (بعد از کلیک روی دکمه گزارش سلامت)."""
    session = get_session(uid)
    session["active_flow"] = "health"
    session["current_question_id"] = get_first_question_id()
    session["prev_question_id"] = None
    # ارسال پیام شروع (اختیاری)
    await context.bot.send_message(
        chat_id=uid,
        text="🩺 <b>شروع ارزیابی سلامت پت</b>\n\n📝 الان چند تا سؤال می‌پرسم.\n⏱ حدود ۵ تا ۱۰ دقیقه وقتت رو می‌گیره.\n\n❌ هر لحظه می‌تونی «انصراف و بازگشت» رو بزنی.\n\nبزن بریم! 👇",
        parse_mode="HTML",
    )
    return await send_question(uid, context)

async def send_question(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ارسال سؤال فعلی به کاربر."""
    session = get_session(uid)
    qid = session["current_question_id"]

    if qid is None:
        return MAIN_MENU

    question = get_question_by_id(qid)
    if not question:
        logger.error(f"Question ID {qid} not found!")
        return MAIN_MENU

    answers = session["answers"]

    # نمایش پیام تغییر بخش در صورت نیاز
    transition_msg = should_show_section_transition(
        qid, session.get("prev_question_id"), answers
    )
    if transition_msg:
        await context.bot.send_message(chat_id=uid, text=transition_msg, parse_mode="HTML")

    # پیشرفت
    progress = calculate_progress(qid, answers)
    pet_name = answers.get("pet_name", "پتت")
    q_text = question["text"].replace("{pet_name}", pet_name)
    text = f"{progress}\n\n{q_text}"
    if question.get("micro_copy"):
        text += f"\n\n{question['micro_copy']}"

    q_type = question["type"]
    options = get_options_for_question(question, answers)

    if q_type == "text_input":
        if options:  # مثلاً سوال 33 که هم دکمه داره هم ورودی متن
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

async def handle_health_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """هندل کردن پاسخ‌های تک‌گزينه و متنی/عددی."""
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    if user_text == "❌ انصراف و بازگشت":
        return await cancel_health(update, context)

    session = get_session(uid)
    qid = session.get("current_question_id")
    if qid is None:
        return MAIN_MENU

    question = get_question_by_id(qid)
    if not question:
        return MAIN_MENU

    answers = session["answers"]
    q_type = question["type"]
    variable = question["variable"]

    # بررسی حالت waiting_for_other_text
    if session.get("waiting_for_other_text"):
        other_var = session.get("other_text_variable", variable + "_other")
        answers[other_var] = user_text
        session["waiting_for_other_text"] = False
        session["other_text_variable"] = None
        await update.message.reply_text(f"✅ ثبت شد: {user_text}")
        return await advance(uid, context)

    # Text input با گزینه (مثل Q33)
    if q_type == "text_input" and question.get("options"):
        value = find_option_value(question["options"], user_text)
        if value:
            answers[variable] = value
            return await advance(uid, context)
        # اگر دکمه نبود، به عنوان متن آزاد در نظر بگیر
        answers[variable] = user_text
        return await advance(uid, context)

    # Text input ساده
    if q_type == "text_input":
        answers[variable] = user_text
        return await advance(uid, context)

    # Number input
    if q_type == "number_input":
        # پاکسازی اعداد فارسی
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
        return await advance(uid, context)

    # Inline button
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
        return await advance(uid, context)

    return ANSWERING

async def handle_health_multi_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """هندل multi-select."""
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    if user_text == "❌ انصراف و بازگشت":
        return await cancel_health(update, context)

    session = get_session(uid)
    qid = session.get("current_question_id")
    question = get_question_by_id(qid)
    if not question:
        return MAIN_MENU

    answers = session["answers"]
    options = get_options_for_question(question, answers)
    confirm_text = question.get("confirm_button", "✅ تأیید و ادامه")

    if user_text == confirm_text:
        final = session["multi_select_temp"] if session["multi_select_temp"] else ["none"]
        answers[question["variable"]] = final
        session["multi_select_temp"] = []

        # نمایش انتخاب‌ها
        if final != ["none"]:
            selected_texts = [opt["text"] for opt in options if opt["value"] in final]
            if selected_texts:
                await update.message.reply_text("✅ انتخاب‌های شما:\n" + "\n".join(f"  • {t}" for t in selected_texts))

        if "_other" in final and question.get("has_other_text"):
            session["waiting_for_other_text"] = True
            session["other_text_variable"] = question["variable"] + "_detail"
            await update.message.reply_text("✏️ لطفاً جزئیات رو بنویس:", reply_markup=cancel_only_keyboard())
            return ANSWERING

        return await advance(uid, context)

    # Toggle option
    value = find_option_value(options, user_text)
    if value is None:
        await update.message.reply_text("⚠️ لطفاً یکی از گزینه‌ها رو انتخاب کن.")
        return MULTI_SELECT

    temp = session["multi_select_temp"]
    exclusive = {"none", "all_normal", "nothing", "healthy", "dont_remember"}
    if value in exclusive:
        session["multi_select_temp"] = [value]
    else:
        # حذف مقادیر انحصاری
        for ev in exclusive:
            if ev in temp:
                temp.remove(ev)
        if value in temp:
            temp.remove(value)
        else:
            temp.append(value)

    # بازفرستادن سؤال با کیبورد به‌روز
    progress = calculate_progress(qid, answers)
    pet_name = answers.get("pet_name", "پتت")
    q_text = question["text"].replace("{pet_name}", pet_name)
    text = f"{progress}\n\n{q_text}"
    if question.get("micro_copy"):
        text += f"\n\n{question['micro_copy']}"
    kb = build_multi_select_keyboard(options, session["multi_select_temp"], confirm_text)
    await update.message.reply_text(text=text, reply_markup=kb, parse_mode="HTML")
    return MULTI_SELECT

async def advance(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    """رفتن به سؤال بعدی یا پایان."""
    session = get_session(uid)
    current_id = session["current_question_id"]
    answers = session["answers"]

    next_id = get_next_question_id(current_id, answers)
    if next_id is None:
        return await finish_health(uid, context)
    else:
        session["prev_question_id"] = current_id
        session["current_question_id"] = next_id
        return await send_question(uid, context)

async def finish_health(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    """پایان ارزیابی و ارسال به ادمین."""
    session = get_session(uid)

    # گرفتن اطلاعات کاربر
    try:
        chat = await context.bot.get_chat(uid)
        full_name = chat.full_name or "ناشناس"
        username = f"@{chat.username}" if chat.username else "ندارد"
    except:
        full_name = "خطا"
        username = "خطا"

    prompt = generate_health_prompt(session["answers"])
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    header = (
        f"🔔 ارزیابی جدید دریافت شد!\n"
        f"{'─'*30}\n"
        f"👤 نام: {full_name}\n"
        f"🆔 یوزرنیم: {username}\n"
        f"🔢 Chat ID: {uid}\n"
        f"⏰ زمان: {now}\n"
        f"📊 تعداد پاسخ‌ها: {len(session['answers'])}\n"
        f"{'─'*30}\n"
        f"💡 برای ارسال PDF، روی این پیام Reply کن.\n"
        f"{'─'*30}\n"
    )

    full_msg = header + "\n" + prompt
    # ارسال به ادمین (تکه‌تکه)
    for i in range(0, len(full_msg), 4000):
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=full_msg[i:i+4000])

    # پیام پایان به کاربر
    await context.bot.send_message(
        chat_id=uid,
        text="✅ ممنون! گزارش سلامت پتت داره آماده می‌شه.\n🕐 تا ۲۴ ساعت آینده برات ارسال میشه.",
        reply_markup=get_main_menu_keyboard(),
    )

    reset_session(uid)
    return MAIN_MENU

async def cancel_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """لغو ارزیابی و بازگشت به منو."""
    uid = update.effective_user.id
    reset_session(uid)
    await update.message.reply_text(
        "❌ ارزیابی لغو شد.\n🏠 برگشتی به منوی اصلی 👇",
        reply_markup=get_main_menu_keyboard(),
    )
    return MAIN_MENU
