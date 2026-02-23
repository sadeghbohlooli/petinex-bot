"""
handlers/admin.py
Admin reply handler – forwards files / photos / messages to users.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_CHAT_ID

logger = logging.getLogger(__name__)


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
