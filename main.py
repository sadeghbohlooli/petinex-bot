"""
Petinex Bot — Main Entry Point
================================
فقط wiring — هیچ منطقی اینجا نیست.
"""

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

from config import BOT_TOKEN, ADMIN_CHAT_ID
from core.states import MAIN_MENU, ANSWERING, MULTI_SELECT
from core.menu import handle_main_menu
from handlers.commands import (
    cmd_start, cmd_health, cmd_diet, cmd_support, cmd_stats, post_init,
)
from handlers.answer import handle_health_answer, handle_health_multi_select
from handlers.admin import admin_reply_handler
from questions import get_total_all_questions, get_total_base_questions


def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not set!")
        return
    if not ADMIN_CHAT_ID:
        print("❌ ADMIN_CHAT_ID not set!")
        return

    print("🚀 Starting Petinex Bot...")
    print(
        f"📋 Total questions: {get_total_all_questions()} "
        f"({get_total_base_questions()} base + "
        f"{get_total_all_questions() - get_total_base_questions()} conditional)"
    )

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
                    handle_health_answer,
                ),
            ],
            MULTI_SELECT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    handle_health_multi_select,
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
