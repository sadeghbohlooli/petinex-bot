"""توابع کمکی مشترک."""


def persian_to_western(text: str) -> str:
    """تبدیل ارقام فارسی/عربی به انگلیسی و نرمال‌سازی اعشار."""
    cleaned = text.replace(",", ".").replace("٫", ".").replace("،", ".")
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    arabic_digits = "٠١٢٣٤٥٦٧٨٩"
    for i, (p, a) in enumerate(zip(persian_digits, arabic_digits)):
        cleaned = cleaned.replace(p, str(i)).replace(a, str(i))
    return cleaned
