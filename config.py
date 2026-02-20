import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
USER_TIMEOUT = 3600
DEBUG_MODE = os.environ.get("DEBUG_MODE", "False").lower() == "true"
