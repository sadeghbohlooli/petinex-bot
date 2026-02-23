# core/keyboards.py
"""ساخت کیبوردهای reply — مستقل از flow خاص."""
from telegram import ReplyKeyboardMarkup, KeyboardButton


def build_option_keyboard(options: list, cancel_btn: bool = True, one_time: bool = True) -> ReplyKeyboardMarkup:
    """
    ساخت کیبورد از لیست optionها (هر option: {"text": ..., "value": ...})
    options: لیست دیکشنری‌های دارای کلید text
    """
    rows = []
    row = []
    for opt in options:
        row.append(KeyboardButton(opt["text"]))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    if cancel_btn:
        rows.append([KeyboardButton("❌ انصراف و بازگشت")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=one_time)


def build_multi_select_keyboard(options: list, selected: list, confirm_text: str = "✅ تأیید و ادامه") -> ReplyKeyboardMarkup:
    """ساخت کیبورد multi-select با چکمارک."""
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
    rows.append([KeyboardButton(confirm_text)])
    rows.append([KeyboardButton("❌ انصراف و بازگشت")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def cancel_only_keyboard() -> ReplyKeyboardMarkup:
    """کیبوردی که فقط دکمه انصراف دارد."""
    return ReplyKeyboardMarkup(
        [[KeyboardButton("❌ انصراف و بازگشت")]],
        resize_keyboard=True,
    )


def find_option_value(options: list, user_text: str) -> str | None:
    """پیدا کردن value یک گزینه از روی متن کاربر (با یا بدون چکمارک)."""
    clean = user_text.replace(" ✅", "").strip()
    for opt in options:
        if opt["text"] == clean or opt["text"] == user_text:
            return opt["value"]
    return None
