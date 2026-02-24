# core/session.py
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from database.crud import get_user_by_telegram_id, get_pets_by_user_id

user_sessions = {}

async def load_user_to_session(uid: int, telegram_id: int):
    """بارگذاری اطلاعات کاربر از دیتابیس به session"""
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        return False
    pets = await get_pets_by_user_id(user["id"])
    if uid not in user_sessions:
        user_sessions[uid] = {
            "active_flow": None,
            "current_question_id": None,
            "prev_question_id": None,
            "answers": {},
            "multi_select_temp": [],
            "waiting_for_other_text": False,
            "other_text_variable": None,
            "started_at": datetime.now().isoformat(),
            "user_id": user["id"],
            "pets": pets,
            "user_data": user,
        }
    else:
        user_sessions[uid]["user_id"] = user["id"]
        user_sessions[uid]["pets"] = pets
        user_sessions[uid]["user_data"] = user
    return True

async def ensure_user_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> dict:
    """اطمینان از اینکه session کاربر وجود داره و از دیتابیس لود شده"""
    uid = update.effective_user.id
    if uid not in user_sessions:
        loaded = await load_user_to_session(uid, uid)
        if not loaded:
            user_sessions[uid] = {
                "active_flow": None,
                "current_question_id": None,
                "prev_question_id": None,
                "answers": {},
                "multi_select_temp": [],
                "waiting_for_other_text": False,
                "other_text_variable": None,
                "started_at": datetime.now().isoformat(),
                "user_id": None,
                "pets": [],
                "user_data": None,
            }
    return user_sessions[uid]

def get_session(uid: int) -> dict:
    """دریافت session (بدون لود - فقط برای مواقعی که مطمئنیم وجود داره)"""
    return user_sessions.get(uid, {})

def reset_session(uid: int):
    user_sessions.pop(uid, None)

def get_all_sessions() -> dict:
    return user_sessions

async def update_session_pets(uid: int):
    if uid in user_sessions and user_sessions[uid].get("user_id"):
        pets = await get_pets_by_user_id(user_sessions[uid]["user_id"])
        user_sessions[uid]["pets"] = pets
