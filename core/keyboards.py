"""
core/keyboards.py
─────────────────
توابع ساخت کیبورد (منوی اصلی + سؤالات تکی + چندانتخابی).
کپی دقیق از main.py اصلی — بدون هیچ تغییری.
"""

from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from questions import get_options_for_question

from core.menu import (
    BTN_HEALTH_REPORT,
    BTN_DIET,
    BTN_VET_ONLINE,
    BTN_CLINIC,
    BTN_PET_SHOP,
    BTN_BOARDING,
    BTN_PHARMACY,
    BTN_GROOMER,
    BTN_TRAINER,
    BTN_EDUCATION,
    BTN_SUPPORT,
)


# ============================================================
# KEYBOARD BUILDERS
# ============================================================

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build the persistent main menu keyboard."""
    keyboard = [
        [KeyboardButton(BTN_HEALTH_REPORT)],
        [KeyboardButton(BTN_DIET), KeyboardButton(BTN_VET_ONLINE)],
        [KeyboardButton(BTN_CLINIC), KeyboardButton(BTN_PET_SHOP)],
        [KeyboardButton(BTN_BOARDING), KeyboardButton(BTN_PHARMACY)],
        [KeyboardButton(BTN_GROOMER), KeyboardButton(BTN_TRAINER)],
        [KeyboardButton(BTN_EDUCATION)],
        [KeyboardButton(BTN_SUPPORT)],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def build_reply_keyboard(question: dict, user_answers: dict) -> ReplyKeyboardMarkup:
    """
    Build a ReplyKeyboardMarkup from question options.
    Handles conditional_options based on user_answers.
    """
    options = get_options_for_question(question, user_answers)
    if not options:
        # Fallback: just cancel button
        return ReplyKeyboardMarkup(
            [[KeyboardButton("❌ انصراف و بازگشت")]],
            resize_keyboard=True,
        )

    rows = []
    row = []
    for opt in options:
        row.append(KeyboardButton(opt["text"]))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([KeyboardButton("❌ انصراف و بازگشت")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)


def build_multi_reply_keyboard(
    question: dict, selected: list, user_answers: dict
) -> ReplyKeyboardMarkup:
    """Build keyboard for multi-select with checkmarks and confirm button."""
    options = get_options_for_question(question, user_answers)
    if not options:
        return ReplyKeyboardMarkup(
            [[KeyboardButton("❌ انصراف و بازگشت")]],
            resize_keyboard=True,
        )

    rows = []
    row = []
    for opt in options:
        check = " ✅" if opt["value"] in selected else ""
        row.append(KeyboardButton(opt["text"] + check))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    confirm_text = question.get("confirm_button", "✅ تأیید و ادامه")
    rows.append([KeyboardButton(confirm_text)])
    rows.append([KeyboardButton("❌ انصراف و بازگشت")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=False)


def find_option_value(question: dict, user_text: str, user_answers: dict) -> str | None:
    """Find the option value matching the user's text (with or without checkmark)."""
    clean_text = user_text.replace(" ✅", "").strip()
    options = get_options_for_question(question, user_answers)
    if not options:
        return None
    for opt in options:
        if opt["text"] == clean_text or opt["text"] == user_text:
            return opt["value"]
    return None
