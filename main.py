import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
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
    WELCOME_MESSAGE,
    START_BUTTON_TEXT,
    TRANSITIONS,
    COMPLETION_MESSAGE,
    get_question_by_id,
    get_total_questions,
)
from prompt_template import generate_prompt

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Conversation States ───
WAITING_START = 0
ANSWERING = 1
MULTI_SELECT = 2

user_sessions = {}


def get_session(uid: int) -> dict:
    if uid not in user_sessions:
        user_sessions[uid] = {
            "current_question": 0,
            "answers": {},
            "multi_select_temp": [],
            "started_at": datetime.now().isoformat(),
        }
    return user_sessions[uid]


def reset_session(uid: int):
    user_sessions.pop(uid, None)


# ─── Build ReplyKeyboard from question options ───
def build_reply_keyboard(question: dict) -> ReplyKeyboardMarkup:
    """Build a ReplyKeyboardMarkup from question options."""
    rows = []
    row = []
    for opt in question["options"]:
        row.append(KeyboardButton(opt["text"]))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)


def build_multi_reply_keyboard(question: dict, selected: list) -> ReplyKeyboardMarkup:
    """Build keyboard for multi-select with checkmarks and confirm button."""
    rows = []
    row = []
    for opt in question["options"]:
        check = " ✅" if opt["value"] in selected else ""
        row.append(KeyboardButton(opt["text"] + check))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    # Add confirm button at the bottom
    confirm_text = question.get("confirm_button", "✅ تأیید و ادامه")
    rows.append([KeyboardButton(confirm_text)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=False)


def find_option_value(question: dict, user_text: str) -> str | None:
    """Find the option value matching the user's text (with or without checkmark)."""
    clean_text = user_text.replace(" ✅", "").strip()
    for opt in question["options"]:
        if opt["text"] == clean_text or opt["text"] == user_text:
            return opt["value"]
    return None


# ─── Send question to user ───
async def send_question(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    session = get_session(uid)
    qid = session["current_question"]
    question = get_question_by_id(qid)
    if not question:
        return ConversationHandler.END

    # Section transition message
    prev_q = get_question_by_id(qid - 1)
    if prev_q is None or prev_q["section"] != question["section"]:
        transition = TRANSITIONS.get(f"section_{question['section']}", "")
        if transition:
            await context.bot.send_message(
                chat_id=uid, text=transition, parse_mode="HTML"
            )

    total = get_total_questions()
    text = f"<b>سؤال {qid} از {total}</b>\n\n{question['text']}"
    if question.get("micro_copy"):
        text += f"\n\n{question['micro_copy']}"

    if question["type"] == "text_input":
        await context.bot.send_message(
            chat_id=uid,
            text=text,
            parse_mode="HTML",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ANSWERING

    elif question["type"] == "multi_select":
        session["multi_select_temp"] = []
        kb = build_multi_reply_keyboard(question, [])
        await context.bot.send_message(
            chat_id=uid, text=text, reply_markup=kb, parse_mode="HTML"
        )
        return MULTI_SELECT

    else:
        # inline_button → now ReplyKeyboard
        kb = build_reply_keyboard(question)
        await context.bot.send_message(
            chat_id=uid, text=text, reply_markup=kb, parse_mode="HTML"
        )
        return ANSWERING


async def advance(uid: int, context: ContextTypes.DEFAULT_TYPE) -> int:
    session = get_session(uid)
    next_id = session["current_question"] + 1
    if next_id > get_total_questions():
        await finish_assessment(uid, context)
        return ConversationHandler.END
    else:
        session["current_question"] = next_id
        return await send_question(uid, context)


# ─── Finish Assessment (unchanged logic) ───
async def finish_assessment(uid: int, context: ContextTypes.DEFAULT_TYPE):
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
        f"{'─' * 30}\n"
        f"💡 برای ارسال PDF، روی این پیام Reply کن و فایل رو بفرست.\n"
        f"{'─' * 30}\n"
    )

    full_msg = header + "\n" + prompt
    chunks = [full_msg[i: i + 4000] for i in range(0, len(full_msg), 4000)]
    for i, chunk in enumerate(chunks):
        prefix = f"📄 بخش {i + 1}/{len(chunks)}:\n\n" if len(chunks) > 1 else ""
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=prefix + chunk)

    await context.bot.send_message(
        chat_id=uid,
        text=COMPLETION_MESSAGE,
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    reset_session(uid)
    logger.info(f"Assessment completed for user {uid} ({full_name})")


# ─── /start Command ───
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.effective_user.id
    reset_session(uid)

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(START_BUTTON_TEXT)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await update.message.reply_text(
        WELCOME_MESSAGE, reply_markup=kb, parse_mode="HTML"
    )
    return WAITING_START


# ─── /stats Command (admin only) ───
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ فقط ادمین دسترسی داره.")
        return
    active = len(user_sessions)
    await update.message.reply_text(
        f"📊 <b>آمار بات</b>\n{'─' * 25}\n👥 Session‌های فعال: {active}",
        parse_mode="HTML",
    )


# ─── Handle "Start" button press ───
async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.effective_user.id
    user_text = update.message.text.strip()

    if user_text == START_BUTTON_TEXT:
        session = get_session(uid)
        session["current_question"] = 1
        return await send_question(uid, context)
    else:
        await update.message.reply_text("👇 لطفاً دکمه شروع رو بزن!")
        return WAITING_START


# ─── Handle Regular Answer (inline_button + text_input) ───
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.effective_user.id
    session = get_session(uid)
    qid = session.get("current_question", 0)
    if qid == 0:
        return ConversationHandler.END

    question = get_question_by_id(qid)
    if not question:
        return ConversationHandler.END

    user_text = update.message.text.strip()

    if question["type"] == "text_input":
        # Validate numeric fields
        if question["variable"] in ("age_months", "weight_kg"):
            cleaned = user_text.replace(",", ".").replace("٫", ".")
            try:
                float(cleaned)
                user_text = cleaned
            except ValueError:
                await update.message.reply_text(
                    "❌ لطفاً یک عدد معتبر وارد کن.\nمثلاً: 8.5 یا 24"
                )
                return ANSWERING

        session["answers"][question["variable"]] = user_text
        return await advance(uid, context)

    elif question["type"] == "inline_button":
        # Find matching option
        value = find_option_value(question, user_text)
        if value is None:
            await update.message.reply_text(
                "⚠️ لطفاً یکی از گزینه‌های موجود رو انتخاب کن!"
            )
            return ANSWERING

        session["answers"][question["variable"]] = value
        return await advance(uid, context)

    return ANSWERING


# ─── Handle Multi-Select Answer ───
async def handle_multi_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    uid = update.effective_user.id
    session = get_session(uid)
    qid = session.get("current_question", 0)
    question = get_question_by_id(qid)

    if not question:
        return ConversationHandler.END

    user_text = update.message.text.strip()
    confirm_text = question.get("confirm_button", "✅ تأیید و ادامه")

    # User pressed confirm button
    if user_text == confirm_text:
        final = session["multi_select_temp"] if session["multi_select_temp"] else ["none"]
        session["answers"][question["variable"]] = final
        session["multi_select_temp"] = []

        # Show final selection summary
        if final != ["none"]:
            selected_texts = []
            for v in final:
                for opt in question["options"]:
                    if opt["value"] == v:
                        selected_texts.append(opt["text"])
            await update.message.reply_text(
                f"✅ انتخاب‌های شما:\n" + "\n".join(f"  • {t}" for t in selected_texts)
            )

        return await advance(uid, context)

    # User selected/deselected an option
    clean_text = user_text.replace(" ✅", "").strip()
    value = None
    for opt in question["options"]:
        if opt["text"] == clean_text:
            value = opt["value"]
            break

    if value is None:
        await update.message.reply_text(
            "⚠️ لطفاً یکی از گزینه‌ها رو انتخاب کن یا دکمه تأیید رو بزن!"
        )
        return MULTI_SELECT

    temp = session["multi_select_temp"]
    if value == "none":
        session["multi_select_temp"] = ["none"]
    else:
        if "none" in temp:
            temp.remove("none")
        if value in temp:
            temp.remove(value)
            # Notify deselection
            await update.message.reply_text(f"❌ حذف شد: {clean_text}")
        else:
            temp.append(value)
            # Notify selection
            await update.message.reply_text(f"✅ اضافه شد: {clean_text}")

    # Resend keyboard with updated checkmarks
    total = get_total_questions()
    text = f"<b>سؤال {qid} از {total}</b>\n\n{question['text']}"
    if question.get("micro_copy"):
        text += f"\n\n{question['micro_copy']}"

    kb = build_multi_reply_keyboard(question, session["multi_select_temp"])
    await update.message.reply_text(
        text=text, reply_markup=kb, parse_mode="HTML"
    )
    return MULTI_SELECT


# ─── Admin Reply Handler (unchanged) ───
async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


# ─── Main ───
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set!")
        return
    if not ADMIN_CHAT_ID:
        print("❌ ADMIN_CHAT_ID not set!")
        return

    print("🚀 Starting Petinex Bot...")

    try:
        app = Application.builder().token(BOT_TOKEN).build()
    except Exception as e:
        print(f"❌ Failed to build application: {e}")
        import sys
        sys.exit(1)

    # Conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            WAITING_START: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_start_button,
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
        fallbacks=[CommandHandler("start", cmd_start)],
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
