# ============================================================
# Petinex Bot — main.py
# Compatible with questions.py v2 (33 base + 8 conditional)
# ============================================================

import logging
from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

from config import BOT_TOKEN, ADMIN_CHAT_ID, DEBUG_MODE
from questions import (
    QUESTIONS,
    QUESTION_FLOW,
    WELCOME_MESSAGE,
    START_BUTTON_TEXT,
    TRANSITIONS,
    COMPLETION_MESSAGE,
    SECTION_BOUNDARIES,
    get_question_by_id,
    get_options_for_question,
    should_show_question,
    get_next_question_id,
    get_section_for_question,
    get_section_transition,
    should_show_section_transition,
    get_first_question_id,
    calculate_progress,
    get_total_questions,
    get_total_base_questions,
    get_total_all_questions,
)
from prompt_template import generate_prompt

# ─── Logging ───
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Conversation States ───
MAIN_MENU = 0
ANSWERING = 1
MULTI_SELECT = 2
OTHER_TEXT = 3       # New state: waiting for free-text after "_other" option

# ─── In-memory sessions ───
user_sessions = {}

# ─── Menu Button Labels ───
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

# ─── Menu Responses ───
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


# ============================================================
# SESSION MANAGEMENT
# ============================================================

def get_session(uid: int) -> dict:
    """Get or create a user session."""
    if uid not in user_sessions:
        user_sessions[uid] = {
            "current_question_id": None,   # Changed: now stores actual question ID (int or str)
            "prev_question_id": None,      # New: track previous question for section transitions
            "answers": {},                 # variable_name → value
            "multi_select_temp": [],       # Temporary multi-select selections
            "waiting_for_other_text": False,  # New: waiting for "_other" free text
            "other_text_variable": None,      # New: which variable to store other text in
            "started_at": datetime.now().isoformat(),
        }
    return user_sessions[uid]


def reset_session(uid: int):
    """Clear a user's session."""
    user_sessions.pop(uid, None)


# ============================================================
# KEYBOARD BUILDERS
# ============================================================

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build the persistent main menu keyboard."""
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


def build_reply_keyboard(question: dict, user_answers: dict) -> ReplyKeyboardMarkup:
    """
    Build a ReplyKeyboardMarkup from question options.
    Handles conditional_options based on user_answers.
    """
    options = get_options_for_question(question, user_answers)
    if not options:
        # Fallback: just cancel button
        return ReplyKeyboardMarkup(
            [[KeyboardButton("❌ انصراف و بازگشت")]],
            resize_keyboard=True,
        )

    rows = []
    row = []
    for opt in options:
        row.append(KeyboardButton(opt["text"]))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([KeyboardButton("❌ انصراف و بازگشت")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)


def build_multi_reply_keyboard(
    question: dict, selected: list, user_answers: dict
) -> ReplyKeyboardMarkup:
    """Build keyboard for multi-select with checkmarks and confirm button."""
    options = get_options_for_question(question, user_answers)
    if not options:
        return ReplyKeyboardMarkup(
            [[KeyboardButton("❌ انصراف و بازگشت")]],
            resize_keyboard=True,
        )

    rows = []
    row = []
    for opt in options:
        check = " ✅" if opt["value"] in selected else ""
        row.append(KeyboardButton(opt["text"] + check))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    confirm_text = question.get("confirm_button", "✅ تأیید و ادامه")
    rows.append([KeyboardButton(confirm_text)])
    rows.append([KeyboardButton("❌ انصراف و بازگشت")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=False)


def find_option_value(question: dict, user_text: str, user_answers: dict) -> str | None:
    """Find the option value matching the user's text (with or without checkmark)."""
    clean_text = user_text.replace(" ✅", "").strip()
    options = get_options_for_question(question, user_answers)
    if not options:
        return None
    for opt in options:
        if opt["text"] == clean_text or opt["text"] == user_text:
            return opt["value"]
    return None


# ============================================================
# PROGRESS DISPLAY
# ============================================================

def get_progress_text(current_id, user_answers: dict) -> str:
    """Generate a progress indicator string."""
    progress = calculate_progress(current_id, user_answers)
    section = get_section_for_question(current_id)

    # Count active questions for display
    active_count = 0
    current_pos = 0
    for qid in QUESTION_FLOW:
        q = get_question_by_id(qid)
        if q and should_show_question(q, user_answers):
            active_count += 1
            if qid == current_id:
                current_pos = active_count

    return f"📊 سؤال {current_pos} از ~{active_count} ({progress}%)"


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

    # Replace {pet_name} placeholder in question text if present
    q_text = question["text"].replace("{pet_name}", pet_name)

    text = f"{progress}\n\n{q_text}"
    if question.get("micro_copy"):
        text += f"\n\n{question['micro_copy']}"

    q_type = question["type"]

    # ── TEXT INPUT ──
    if q_type == "text_input":
        # Some text_input questions also have button options (like Q33)
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
        # Assessment complete
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


# ============================================================
# COMMAND HANDLERS
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


# ============================================================
# MAIN MENU HANDLER
# ============================================================

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


# ============================================================
# CANCEL HANDLER
# ============================================================

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the assessment and return to main menu."""
    uid = update.effective_user.id
    reset_session(uid)

    await update.message.reply_text(
        "❌ ارزیابی لغو شد.\n\n🏠 برگشتی به منوی اصلی 👇",
        reply_markup=get_main_menu_keyboard(),
    )
    return MAIN_MENU


# ============================================================
# ANSWER HANDLER (inline_button + text_input + number_input)
# ============================================================

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle single-choice and text/number input answers."""
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    # Cancel check
    if user_text == "❌ انصراف و بازگشت":
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
        return await advance(uid, context)

    # ── TEXT INPUT ──
    if q_type == "text_input":
        # Check if there are button options too (e.g., Q33 "no concern" button)
        if question.get("options"):
            value = find_option_value(question, user_text, answers)
            if value:
                answers[variable] = value
                return await advance(uid, context)

        # Otherwise treat as free text
        answers[variable] = user_text
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
        return await advance(uid, context)

    return ANSWERING


# ============================================================
# MULTI-SELECT HANDLER
# ============================================================

async def handle_multi_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle multi-select question interactions."""
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    # Cancel check
    if user_text == "❌ انصراف و بازگشت":
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


# ============================================================
# ADMIN REPLY HANDLER
# ============================================================

async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin replies to forward files/messages to users."""
    msg = update.message
    if msg.chat_id != ADMIN_CHAT_ID:
        return
    if not msg.reply_to_message:
        return

    original = msg.reply_to_message.text or ""
    chat_id = None
    for line in original.split("\n"):
        if "Chat ID:" in line:
            try:
                chat_id = int(line.split(":")[-1].strip())
            except ValueError:
                pass

    if not chat_id:
        await msg.reply_text("⚠️ Chat ID پیدا نشد!")
        return

    caption = "📄 گزارش سلامت اختصاصی پت شما آماده شد! 🎉\n\nاگه سؤالی داشتی /start بزن."

    try:
        if msg.document:
            await context.bot.send_document(
                chat_id=chat_id, document=msg.document.file_id, caption=caption
            )
            await msg.reply_text(f"✅ فایل به کاربر {chat_id} ارسال شد!")
        elif msg.photo:
            await context.bot.send_photo(
                chat_id=chat_id, photo=msg.photo[-1].file_id, caption=caption
            )
            await msg.reply_text(f"✅ عکس به کاربر {chat_id} ارسال شد!")
        elif msg.text:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"📩 پیام از تیم Petinex:\n\n{msg.text}",
            )
            await msg.reply_text(f"✅ پیام به کاربر {chat_id} ارسال شد!")
    except Exception as e:
        await msg.reply_text(f"❌ خطا: {e}")


# ============================================================
# BOT MENU COMMANDS (☰ button)
# ============================================================

async def post_init(application):
    """Set bot commands so the ☰ menu button appears in Telegram."""
    commands = [
        BotCommand("start", "🐾 شروع ربات"),
        BotCommand("health", "🩺 گزارش سلامت پت"),
        BotCommand("support", "📞 پشتیبانی سریع"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("✅ Bot menu commands set successfully!")


# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set!")
        return
    if not ADMIN_CHAT_ID:
        print("❌ ADMIN_CHAT_ID not set!")
        return

    print("🚀 Starting Petinex Bot...")
    print(f"📋 Total questions: {get_total_all_questions()} ({get_total_base_questions()} base + {get_total_all_questions() - get_total_base_questions()} conditional)")

    try:
        app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    except Exception as e:
        print(f"❌ Failed to build application: {e}")
        import sys
        sys.exit(1)

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", cmd_start),
            CommandHandler("health", cmd_health),
            CommandHandler("diet", cmd_diet),
            CommandHandler("support", cmd_support),
        ],
        states={
            MAIN_MENU: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_main_menu,
                ),
            ],
            ANSWERING: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_answer,
                ),
            ],
            MULTI_SELECT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_multi_select,
                ),
            ],
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            CommandHandler("health", cmd_health),
            CommandHandler("diet", cmd_diet),
            CommandHandler("support", cmd_support),
        ],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(
        MessageHandler(
            filters.Chat(ADMIN_CHAT_ID)
            & filters.REPLY
            & (filters.Document.ALL | filters.PHOTO | filters.TEXT),
            admin_reply_handler,
        )
    )

    print("✅ Petinex Bot is running!")
    print("📊 Bot is polling for updates...")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message"],
    )


if __name__ == "__main__":
    main()
