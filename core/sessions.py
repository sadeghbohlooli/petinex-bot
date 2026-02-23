"""
core/sessions.py
────────────────
مدیریت session (حافظه موقت) هر کاربر.
کپی دقیق از بخش SESSION MANAGEMENT فایل main.py اصلی.
"""

from datetime import datetime

# ─── ذخیره session همه کاربران ───
user_sessions = {}


def get_session(uid: int) -> dict:
    """Get or create a user session."""
    if uid not in user_sessions:
        user_sessions[uid] = {
            "current_question_id": None,
            "prev_question_id": None,
            "answers": {},
            "multi_select_temp": [],
            "waiting_for_other_text": False,
            "other_text_variable": None,
            "started_at": datetime.now().isoformat(),
        }
    return user_sessions[uid]


def reset_session(uid: int):
    """Clear a user's session."""
    user_sessions.pop(uid, None)
