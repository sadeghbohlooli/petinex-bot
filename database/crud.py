# database/crud.py
import aiosqlite
import json
from datetime import datetime
from .models import DB_PATH

# ------------------- کاربران -------------------

async def get_user_by_telegram_id(telegram_id: int):
    """دریافت کاربر با telegram_id"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

async def create_user(telegram_id: int, first_name: str, username: str = None):
    """ایجاد کاربر جدید با اطلاعات اولیه"""
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            '''INSERT INTO users 
               (telegram_id, first_name, username, joined_at, membership_level) 
               VALUES (?, ?, ?, ?, ?)''',
            (telegram_id, first_name, username, now, 'bronze')
        )
        await db.commit()
        # برگرداندن کاربر ایجاد شده
        new_id = cursor.lastrowid
        return await get_user_by_telegram_id(telegram_id)

async def update_user(telegram_id: int, **kwargs):
    """به‌روزرسانی فیلدهای کاربر (فیلدهای داده شده)"""
    async with aiosqlite.connect(DB_PATH) as db:
        fields = []
        values = []
        for key, val in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(val)
        if not fields:
            return
        values.append(telegram_id)
        await db.execute(
            f'UPDATE users SET {", ".join(fields)} WHERE telegram_id = ?',
            values
        )
        await db.commit()

# ------------------- پت‌ها -------------------

async def get_pets_by_user_id(user_id: int):
    """لیست پت‌های یک کاربر"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM pets WHERE user_id = ? ORDER BY id', (user_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def add_pet(user_id: int, name: str, pet_type: str, breed: str = None, breed_detail: str = None):
    """اضافه کردن پت جدید"""
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            '''INSERT INTO pets 
               (user_id, name, type, breed, breed_detail, created_at, updated_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (user_id, name, pet_type, breed, breed_detail, now, now)
        )
        await db.commit()
        return cursor.lastrowid

# (بقیه توابع مدیریت پت‌ها بعداً اضافه می‌شود)

# ------------------- گزارش‌ها -------------------

async def add_report(pet_id: int, report_type: str, report_data: dict):
    """ذخیره گزارش جدید"""
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        data_json = json.dumps(report_data, ensure_ascii=False)
        await db.execute(
            'INSERT INTO reports (pet_id, report_type, report_data, created_at) VALUES (?, ?, ?, ?)',
            (pet_id, report_type, data_json, now)
        )
        await db.commit()
