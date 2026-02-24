# database/models.py
import aiosqlite
import json
from datetime import datetime

DB_PATH = "petinex.db"

async def init_db():
    """ایجاد جداول اگر وجود نداشته باشند"""
    async with aiosqlite.connect(DB_PATH) as db:
        # جدول کاربران
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                first_name TEXT,
                username TEXT,
                phone TEXT,
                city TEXT,
                email TEXT,
                membership_level TEXT DEFAULT 'bronze',
                joined_at TEXT NOT NULL,
                is_vip INTEGER DEFAULT 0
            )
        ''')
        # جدول پت‌ها
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                breed TEXT,
                breed_detail TEXT,
                age REAL,
                weight REAL,
                medical_history TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        # جدول گزارش‌ها
        await db.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                report_type TEXT NOT NULL,  -- 'basic' یا 'vip'
                report_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE
            )
        ''')
        # جدول تعاملات (اختیاری برای لاگ)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        await db.commit()
