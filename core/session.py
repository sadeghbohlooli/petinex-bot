# core/session.py
from datetime import datetime
from database.crud import get_user_by_telegram_id, get_pets_by_user_id

user_sessions = {}

async def load_user_to_session(uid: int, telegram_id: int):
    """بارگذاری اطلاعات کاربر از دیتابیس به session"""
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        return False
    # کاربر وجود داره، پت‌هاش رو بگیر
    pets = await get_pets_by_user_id(user["id"])
    # ایجاد یا به‌روزرسانی session
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
            "user_id": user["id"],          # id دیتابیس
            "pets": pets,                    # لیست پت‌ها
            "user_data": user,                # کل اطلاعات کاربر (اختیاری)
        }
    else:
        # اگر session از قبل بود، فقط user_id و pets رو آپدیت کن
        user_sessions[uid]["user_id"] = user["id"]
        user_sessions[uid]["pets"] = pets
        user_sessions[uid]["user_data"] = user
    return True

def get_session(uid: int) -> dict:
    """دریافت session (بدون لود از دیتابیس - فرض می‌کنیم از قبل لود شده)"""
    if uid not in user_sessions:
        # اگر نبود، یه موقت می‌سازیم (برای کاربران جدید قبل از عضویت)
        user_sessions[uid] = {
            "active_flow": None,
            "current_question_id": None,
            "prev_question_id": None,
            "answers": {},
            "multi_select_temp": [],
            "waiting_for_other_text": False,
            "other_text_variable": None,
            "started_at": datetime.now().isoformat(),
            "user_id": None,   # یعنی هنوز عضو نشده
            "pets": [],
            "user_data": None,
        }
    return user_sessions[uid]

def reset_session(uid: int):
    """پاک کردن session (برای لغو یا خروج)"""
    user_sessions.pop(uid, None)

def get_all_sessions() -> dict:
    return user_sessions

async def update_session_pets(uid: int):
    """بعد از تغییر در پت‌ها (اضافه/حذف/ویرایش) این تابع رو صدا بزن تا session آپدیت بشه"""
    if uid in user_sessions and user_sessions[uid].get("user_id"):
        pets = await get_pets_by_user_id(user_sessions[uid]["user_id"])
        user_sessions[uid]["pets"] = pets
