import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
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


def build_keyboard(question: dict) -> InlineKeyboardMarkup:
    rows = []
    if question["type"] == "inline_button":
        for opt in question["options"]:
            rows.append(
                [InlineKeyboardButton(
                    text=opt["text"],
                    callback_data=f"a|{question['id']}|{opt['value']}",
                )]
            )
    elif question["type"] == "multi_select":
        for opt in question["options"]:
            rows.append(
                [InlineKeyboardButton(
                    text=opt["text"],
                    callback_data=f"m|{question['id']}|{opt['value']}",
                )]
            )
        rows.append(
            [InlineKeyboardButton(
                text=question.get("confirm_button", "✅ تمام"),
                callback_data=f"done|{question['id']}",
            )]
        )
    return InlineKeyboardMarkup(rows)


def build_multi_keyboard(question: dict, selected: list) -> InlineKeyboardMarkup:
    rows = []
    for opt in question["options"]:
        check = " ✅" if opt["value"] in selected else ""
        rows.append(
            [InlineKeyboardButton(
                text=opt["text"] + check,
                callback_data=f"m|{question['id']}|{opt['value']}",
            )]
        )
    rows.append(
        [InlineKeyboardButton(
            text=question.get("confirm_button", "✅ تمام"),
            callback_data=f"done|{question['id']}",
        )]
    )
    return InlineKeyboardMarkup(rows)


async def send_question(uid: int, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(uid)
    qid = session["current_question"]
    question = get_question_by_id(qid)
    if not question:
        return

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
        await context.bot.send_message(chat_id=uid, text=text, parse_mode="HTML")
    else:
        kb = build_keyboard(question)
        await context.bot.send_message(
            chat_id=uid, text=text, reply_markup=kb, parse_mode="HTML"
        )


async def advance(uid: int, context: ContextTypes.DEFAULT_TYPE):
    session = get_session(uid)
    next_id = session["current_question"] + 1
    if next_id > get_total_questions():
        await finish_assessment(uid, context)
    else:
        session["current_question"] = next_id
        await send_question(uid, context)


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
        chat_id=uid, text=COMPLETION_MESSAGE, parse_mode="HTML"
    )
    reset_session(uid)
    logger.info(f"Assessment completed for user {uid} ({full_name})")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    reset_session(uid)
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton(START_BUTTON_TEXT, callback_data="go")]]
    )
    await update.message.reply_text(
        WELCOME_MESSAGE, reply_markup=kb, parse_mode="HTML"
    )


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ فقط ادمین دسترسی داره.")
        return
    active = len(user_sessions)
    await update.message.reply_text(
        f"📊 <b>آمار بات</b>\n{'─' * 25}\n👥 Session‌های فعال: {active}",
        parse_mode="HTML",
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    data = query.data

    if data == "go":
        session = get_session(uid)
        session["current_question"] = 1
        await send_question(uid, context)
        return

    if data.startswith("a|"):
        parts = data.split("|", 2)
        qid = int(parts[1])
        value = parts[2]
        session = get_session(uid)
        question = get_question_by_id(qid)
        if question:
            session["answers"][question["variable"]] = value
        await advance(uid, context)
        return

    if data.startswith("m|"):
        parts = data.split("|", 2)
        qid = int(parts[1])
        value = parts[2]
        session = get_session(uid)
        question = get_question_by_id(qid)
        if not question:
            return
        temp = session["multi_select_temp"]
        if value == "none":
            session["multi_select_temp"] = ["none"]
        else:
            if "none" in temp:
                temp.remove("none")
            if value in temp:
                temp.remove(value)
            else:
                temp.append(value)
        new_kb = build_multi_keyboard(question, session["multi_select_temp"])
        total = get_total_questions()
        text = f"<b>سؤال {qid} از {total}</b>\n\n{question['text']}"
        if question.get("micro_copy"):
            text += f"\n\n{question['micro_copy']}"
        try:
            await query.edit_message_text(
                text=text, reply_markup=new_kb, parse_mode="HTML"
            )
        except Exception:
            pass
        return

    if data.startswith("done|"):
        parts = data.split("|", 1)
        qid = int(parts[1])
        session = get_session(uid)
        question = get_question_by_id(qid)
        if not question:
            return
        final = session["multi_select_temp"] if session["multi_select_temp"] else ["none"]
        session["answers"][question["variable"]] = final
        session["multi_select_temp"] = []
        await advance(uid, context)
        return


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    session = get_session(uid)
    qid = session.get("current_question", 0)
    if qid == 0:
        return
    question = get_question_by_id(qid)
    if not question or question["type"] != "text_input":
        return
    text = update.message.text.strip()
    if question["variable"] in ("age_months", "weight_kg"):
        cleaned = text.replace(",", ".").replace("٫", ".")
        try:
            float(cleaned)
            text = cleaned
        except ValueError:
            await update.message.reply_text(
                "❌ لطفاً یک عدد معتبر وارد کن.\nمثلاً: 8.5 یا 24"
            )
            return
    session["answers"][question["variable"]] = text
    await advance(uid, context)


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


def main():
    """Start the bot"""
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

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~filters.Chat(ADMIN_CHAT_ID),
            text_handler,
        )
    )
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
        allowed_updates=["message", "callback_query"],
    )


if __name__ == "__main__":
    main()
