import aiosqlite
from datetime import datetime

DB_NAME = "database.db"

# --- BAZA YARATISH ---
async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS workers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            telegram_id INTEGER UNIQUE
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id INTEGER,
            summa TEXT,
            quantity TEXT,
            description TEXT,
            created_at TEXT
        )
        """)
        await db.commit()

# --- ISHCHI QO‘SHISH ---
async def add_worker(name, phone, telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO workers (name, phone, telegram_id) VALUES (?, ?, ?)",
            (name, phone, telegram_id)
        )
        await db.commit()

# --- ISHCHILARNI OLISH ---
async def get_workers():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM workers") as cursor:
            return await cursor.fetchall()

# --- ISHCHI BOR-YO‘QLIGINI TEKSHIRISH ---
async def check_worker(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT * FROM workers WHERE telegram_id = ?",
            (telegram_id,)
        ) as cursor:
            return await cursor.fetchone()

# --- ISHCHI O'CHIRISH ---
async def delete_worker_by_telegram_id(telegram_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM workers WHERE telegram_id = ?",
            (telegram_id,)
        )
        await db.commit()

# --- HISOBOT QO‘SHISH ---
async def add_report(worker_id, summa, quantity, description, created_at):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO reports (worker_id, summa, quantity, description, created_at) VALUES (?, ?, ?, ?, ?)",
            (worker_id, summa, quantity, description, created_at)
        )
        await db.commit()

# --- BUGUNGI HISOBOTLARNI OLISH ---
async def get_todays_reports():
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT * FROM reports WHERE DATE(created_at) = ?",
            (today,)
        ) as cursor:
            return await cursor.fetchall()

# --- UMUMIY HISOBOTLARNI OLISH ---
async def get_all_reports():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM reports") as cursor:
            return await cursor.fetchall()
