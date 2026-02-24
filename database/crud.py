# database/crud.py
import aiosqlite
import json
from datetime import datetime
from .models import DB_PATH

# ------------------- کاربران -------------------
async def get_user_by_telegram_id(telegram_id: int):
    """گرفتن کاربر با telegram_id"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

async def create_user(telegram_id: int, first_name: str, username: str = None, phone: str = None):
    """ایجاد کاربر جدید و برگردوندن id"""
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            'INSERT INTO users (telegram_id, first_name, username, phone, joined_at) VALUES (?, ?, ?, ?, ?)',
            (telegram_id, first_name, username, phone, now)
        )
        await db.commit()
        return cursor.lastrowid

async def update_user_phone(telegram_id: int, phone: str):
    """آپدیت شماره تلفن کاربر"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET phone = ? WHERE telegram_id = ?', (phone, telegram_id))
        await db.commit()

# ------------------- پت‌ها -------------------
async def get_pets_by_user_id(user_id: int):
    """گرفتن لیست پت‌های یه کاربر"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM pets WHERE user_id = ? ORDER BY id', (user_id,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def get_pet_by_id(pet_id: int):
    """گرفتن یه پت با id"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM pets WHERE id = ?', (pet_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

async def add_pet(user_id: int, name: str, pet_type: str, breed: str = None, breed_detail: str = None):
    """اضافه کردن پت جدید"""
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            'INSERT INTO pets (user_id, name, type, breed, breed_detail, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, name, pet_type, breed, breed_detail, now)
        )
        await db.commit()
        return cursor.lastrowid

async def update_pet(pet_id: int, name: str = None, pet_type: str = None, breed: str = None, breed_detail: str = None):
    """ویرایش اطلاعات پت (فیلدهایی که None نباشن آپدیت می‌شن)"""
    async with aiosqlite.connect(DB_PATH) as db:
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if pet_type is not None:
            updates.append("type = ?")
            params.append(pet_type)
        if breed is not None:
            updates.append("breed = ?")
            params.append(breed)
        if breed_detail is not None:
            updates.append("breed_detail = ?")
            params.append(breed_detail)
        if not updates:
            return
        params.append(pet_id)
        await db.execute(f'UPDATE pets SET {", ".join(updates)} WHERE id = ?', params)
        await db.commit()

async def delete_pet(pet_id: int):
    """حذف یه پت"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM pets WHERE id = ?', (pet_id,))
        await db.commit()

# ------------------- گزارش‌ها (برای آینده) -------------------
async def add_report(pet_id: int, report_data: dict):
    """ذخیره یه گزارش جدید"""
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now().isoformat()
        data_json = json.dumps(report_data, ensure_ascii=False)
        await db.execute(
            'INSERT INTO reports (pet_id, report_data, created_at) VALUES (?, ?, ?)',
            (pet_id, data_json, now)
        )
        await db.commit()

async def get_reports_by_pet_id(pet_id: int):
    """گرفتن همه گزارش‌های یه پت"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM reports WHERE pet_id = ? ORDER BY created_at DESC', (pet_id,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
