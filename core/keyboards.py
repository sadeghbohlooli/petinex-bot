# core/keyboards.py
from telegram import ReplyKeyboardMarkup, KeyboardButton

def build_option_keyboard(options, cancel_btn=True, one_time=True):
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

def build_multi_select_keyboard(options, selected, confirm_text="✅ تأیید و ادامه"):
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

def cancel_only_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("❌ انصراف و بازگشت")]],
        resize_keyboard=True,
    )

def find_option_value(options, user_text):
    clean = user_text.replace(" ✅", "").strip()
    for opt in options:
        if opt["text"] == clean or opt["text"] == user_text:
            return opt["value"]
    return None
