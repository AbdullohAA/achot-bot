import sqlite3
from datetime import datetime

DB_PATH = "otchot.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        name TEXT,
        added_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_tg_id INTEGER,
        worker_name TEXT,
        text TEXT,
        amount REAL,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_worker(tg_id: int, name: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO workers (tg_id, name, added_at) VALUES (?, ?, ?)", (tg_id, name, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_workers():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT tg_id, name, added_at FROM workers")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_report(worker_tg_id: int, worker_name: str, text: str, amount: float = 0.0):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO reports (worker_tg_id, worker_name, text, amount, created_at) VALUES (?, ?, ?, ?, ?)", (worker_tg_id, worker_name, text, amount, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def get_reports_by_date(date_str: str):
    # date_str in YYYY-MM-DD
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports WHERE created_at LIKE ? ORDER BY created_at DESC", (f"{date_str}%",))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_reports():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_reports_by_worker(tg_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reports WHERE worker_tg_id = ? ORDER BY created_at DESC", (tg_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]