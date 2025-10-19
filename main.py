import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import BOT_TOKEN, ADMIN_ID
import database as db
from datetime import date

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# vaqtincha xotirada foydalanuvchi harakati
pending_actions = {}  # user_id -> action

# foydalanuvchi menyusi
worker_kb = ReplyKeyboardMarkup(resize_keyboard=True)
worker_kb.add(KeyboardButton("Sotuv qo'shish"))
worker_kb.add(KeyboardButton("Mening otchotlarim"))

# admin menyusi
admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add(KeyboardButton("Ishchi qo'shish"))
admin_kb.add(KeyboardButton("Bugungi achotlar"))
admin_kb.add(KeyboardButton("Umumiy achotlar"))

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    db.create_db()
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        await message.reply("👋 Assalomu alaykum, Admin!\nMenyuni tanlang:", reply_markup=admin_kb)
    else:
        await message.reply("Salom! Hisobot yuborish uchun menyudan tanlang:", reply_markup=worker_kb)

@dp.message_handler(lambda m: m.text == "Ishchi qo'shish")
async def add_worker_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("⛔ Bu buyruq faqat admin uchun.")
        return
    pending_actions[message.from_user.id] = "await_add_worker"
    await message.reply("Qo'shmoqchi bo'lgan ishchining Telegram ID sini yuboring.\nYoki profilini forward qiling:", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(lambda message: message.forward_from is not None and pending_actions.get(message.from_user.id) == 'await_add_worker')
async def add_worker_from_forward(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    f = message.forward_from
    tg_id = f.id
    name = f.username or f.first_name or 'NoName'
    db.add_worker(tg_id, name)
    pending_actions.pop(message.from_user.id, None)
    await message.reply(f"Ishchi qo'shildi ✅\n👤 {name} ({tg_id})", reply_markup=admin_kb)

@dp.message_handler(lambda message: pending_actions.get(message.from_user.id) == 'await_add_worker')
async def add_worker_by_id(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.strip()
    parts = text.split(maxsplit=1)
    try:
        tg_id = int(parts[0])
    except:
        await message.reply("Iltimos, to‘g‘ri Telegram ID yuboring. Masalan: 123456789", reply_markup=admin_kb)
        return
    name = parts[1] if len(parts) > 1 else f"User_{tg_id}"
    db.add_worker(tg_id, name)
    pending_actions.pop(message.from_user.id, None)
    await message.reply(f"Ishchi qo‘shildi ✅\n👤 {name} ({tg_id})", reply_markup=admin_kb)

@dp.message_handler(lambda m: m.text == "Sotuv qo'shish")
async def start_report(message: types.Message):
    pending_actions[message.from_user.id] = "await_report"
    await message.reply("Hisobot matnini yuboring.\nMasalan: `3 ta krossovka sotildi, summa:1500000`", reply_markup=ReplyKeyboardRemove())

@dp.message_handler(lambda m: pending_actions.get(m.from_user.id) == "await_report")
async def save_report(message: types.Message):
    user = message.from_user
    text = message.text
    amount = 0.0
    import re
    m = re.search(r"(?:summa|amount)\s*[:\-]?\s*(\d+[\d\s.]*)", text.lower())
    if m:
        amt_str = m.group(1).replace(' ', '').replace('.', '')
        try:
            amount = float(amt_str)
        except:
            amount = 0.0
    db.add_report(user.id, user.username or user.first_name or 'NoName', text, amount)
    pending_actions.pop(message.from_user.id, None)
    await message.reply("✅ Hisobot qabul qilindi!", reply_markup=worker_kb)
    try:
        await bot.send_message(ADMIN_ID, f"📥 Yangi otchot:\n👤 {user.username or user.first_name}\n{text}\n💰 Summa: {amount}")
    except:
        pass

@dp.message_handler(lambda m: m.text == "Mening otchotlarim")
async def my_reports(message: types.Message):
    reps = db.get_reports_by_worker(message.from_user.id)
    if not reps:
        await message.reply("Sizda hali otchot yo‘q.", reply_markup=worker_kb)
        return
    text = "🧾 Sizning so‘nggi 10 ta otchotingiz:\n\n"
    for r in reps[:10]:
        text += f"{r['created_at'][:19]} — {r['text']} — 💰 {r.get('amount') or 0}\n"
    await message.reply(text, reply_markup=worker_kb)

@dp.message_handler(lambda m: m.text == "Bugungi achotlar")
async def today_reports(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    today = date.today().isoformat()
    reps = db.get_reports_by_date(today)
    if not reps:
        await message.reply("Bugun uchun otchot yo‘q.", reply_markup=admin_kb)
        return
    text = f"📅 {today} — Bugungi otchotlar:\n\n"
    total = 0
    for r in reps:
        amt = r.get('amount') or 0
        total += amt
        text += f"{r['worker_name']}: {r['text']} — 💰 {amt}\n"
    text += f"\nJami: 💰 {total}"
    await message.reply(text, reply_markup=admin_kb)

@dp.message_handler(lambda m: m.text == "Umumiy achotlar")
async def all_reports(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    reps = db.get_all_reports()
    if not reps:
        await message.reply("Hozircha otchotlar yo‘q.", reply_markup=admin_kb)
        return
    text = "📚 So‘nggi 20 ta otchot:\n\n"
    total = 0
    for r in reps[:20]:
        amt = r.get('amount') or 0
        total += amt
        text += f"{r['created_at'][:19]} — {r['worker_name']}: {r['text']} — 💰 {amt}\n"
    text += f"\nJami: 💰 {total}"
    await message.reply(text, reply_markup=admin_kb)

@dp.message_handler()
async def fallback(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("Admin menyu:", reply_markup=admin_kb)
    else:
        await message.reply("Foydalanuvchi menyu:", reply_markup=worker_kb)

if __name__ == "__main__":
    print("🤖 Bot ishga tushmoqda...")
    db.create_db()
    executor.start_polling(dp, skip_updates=True)
