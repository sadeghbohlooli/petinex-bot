"""مدیریت session کاربران — مستقل از هر flow."""

from datetime import datetime

user_sessions = {}


def get_session(uid: int) -> dict:
    """Get or create a user session."""
    if uid not in user_sessions:
        user_sessions[uid] = {
            "active_flow": None,              # "health", "diet", "vet", ...
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
