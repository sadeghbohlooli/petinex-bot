import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters

from config import BOT_TOKEN, ADMIN_CHAT_ID, DEBUG_MODE
from core.states import MAIN_MENU, ANSWERING, MULTI_SELECT
from core.menu import handle_main_menu
from handlers.commands import cmd_start, cmd_health, cmd_diet, cmd_support, cmd_stats, post_init
from handlers.admin import admin_reply_handler
from flows.health_flow import handle_health_answer, handle_health_multi_select
from database.models import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
)

def main():
    # مقداردهی اولیه دیتابیس
    asyncio.run(init_db())
    print("✅ Database initialized.")

    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        print("❌ BOT_TOKEN or ADMIN_CHAT_ID not set!")
        return

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", cmd_start),
            CommandHandler("health", cmd_health),
            CommandHandler("diet", cmd_diet),
            CommandHandler("support", cmd_support),
        ],
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu),
            ],
            ANSWERING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_health_answer),
            ],
            MULTI_SELECT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_health_multi_select),
            ],
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            CommandHandler("health", cmd_health),
        ],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(
        MessageHandler(
            filters.Chat(ADMIN_CHAT_ID) & filters.REPLY & (filters.Document.ALL | filters.PHOTO | filters.TEXT),
            admin_reply_handler,
        )
    )

    print("✅ Petinex Bot (modular) is running!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
