import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_ID
from database import (
    create_db, add_worker, get_workers, check_worker,
    add_report, get_todays_reports, get_all_reports, delete_worker_by_telegram_id
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- FSM holatlari ---
class AddWorker(StatesGroup):
    name = State()
    phone = State()
    telegram_id = State()

class ReportState(StatesGroup):
    summa = State()
    quantity = State()
    description = State()

# --- Klaviaturalar ---
admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👷 Ishchi qo‘shish"), KeyboardButton(text="👥 Mening ishchilarim")],
        [KeyboardButton(text="📊 Bugungi hisobotlar"), KeyboardButton(text="📈 Umumiy hisobotlar")],
        [KeyboardButton(text="📩 Ishchiga eslatma yuborish"), KeyboardButton(text="👢 Ishchini o'chirish")]
    ],
    resize_keyboard=True
)

worker_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🧾 Hisobot yuborish")]],
    resize_keyboard=True
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⬅️ Orqaga")]],
    resize_keyboard=True
)

# --- /start komandasi ---
@dp.message(lambda m: m.text == "/start")
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await create_db()
    if message.from_user.id == ADMIN_ID:
        await message.answer("👋 Assalomu alaykum, Admin 👑", reply_markup=admin_kb)
    else:
        worker = await check_worker(message.from_user.id)
        if worker:
            await message.answer(f"👋 Assalomu alaykum, {worker[1]}!\nHisobot yuborish uchun menyudan foydalaning 👇",
                                 reply_markup=worker_kb)
        else:
            await message.answer("❌ Siz ro‘yxatda yo‘qsiz. Admin sizni qo‘shmaguncha botdan foydalana olmaysiz.")

# --- Orqaga ---
@dp.message(lambda m: m.text == "⬅️ Orqaga")
async def back_to_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("⬅️ Asosiy menyu:", reply_markup=admin_kb if message.from_user.id == ADMIN_ID else worker_kb)

# --- Ishchini o'chirish ---
@dp.message(lambda m: m.text == "👢 Ishchini o'chirish")
async def remove_worker_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ Bu bo‘lim faqat admin uchun.")
    workers = await get_workers()
    if not workers:
        return await message.reply("📭 Hozircha ishchi yo‘q.", reply_markup=admin_kb)

    for w in workers:
        name = w[1]
        phone = w[2]
        tg_id = w[3]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ O'chirish", callback_data=f"del:{tg_id}"),
                InlineKeyboardButton(text="🔙 Bekor", callback_data="cancel")
            ]
        ])
        await message.reply(f"👤 {name}\n📞 {phone}\n🆔 {tg_id}", reply_markup=kb)

@dp.callback_query(lambda c: c.data and c.data.startswith("del:"))
async def confirm_delete_callback(callback: types.CallbackQuery):
    await callback.answer()
    tg_id = callback.data.split(":", 1)[1]
    confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, o'chir", callback_data=f"confirm_del:{tg_id}"),
            InlineKeyboardButton(text="❎ Bekor", callback_data="cancel")
        ]
    ])
    await callback.message.reply(f"⚠️ Ishchi (ID: {tg_id}) ni o'chirishni xohlaysizmi? Tasdiqlaysizmi?", reply_markup=confirm_kb)

@dp.callback_query(lambda c: c.data and c.data.startswith("confirm_del:"))
async def do_delete_callback(callback: types.CallbackQuery):
    await callback.answer()
    tg_id = int(callback.data.split(":", 1)[1])
    await delete_worker_by_telegram_id(tg_id)
    try:
        await callback.message.reply(f"✅ Ishchi (ID: {tg_id}) muvaffaqiyatli o'chirildi.", reply_markup=admin_kb)
    except:
        pass

@dp.callback_query(lambda c: c.data == "cancel")
async def cancel_callback(callback: types.CallbackQuery):
    await callback.answer("Bekor qilindi", show_alert=False)
    try:
        await callback.message.reply("❎ Amal bekor qilindi.", reply_markup=admin_kb)
    except:
        pass

# --- Ishchi qo‘shish ---
@dp.message(lambda m: m.text == "👷 Ishchi qo‘shish")
async def add_worker_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ Sizda bu amalni bajarish huquqi yo‘q.")
    await state.set_state(AddWorker.name)
    await message.reply("🧑‍💼 Yangi ishchining ismini kiriting:", reply_markup=back_kb)

@dp.message(AddWorker.name)
async def add_worker_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("📞 Endi ishchining telefon raqamini kiriting:")
    await state.set_state(AddWorker.phone)

@dp.message(AddWorker.phone)
async def add_worker_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.reply("📲 Endi ishchining Telegram ID raqamini kiriting:")
    await state.set_state(AddWorker.telegram_id)

@dp.message(AddWorker.telegram_id)
async def add_worker_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name, phone = data.get("name"), data.get("phone")
    try:
        telegram_id = int(message.text)
    except ValueError:
        return await message.reply("⚠️ Noto‘g‘ri ID. Faqat raqam kiriting.")
    await add_worker(name, phone, telegram_id)
    await message.reply(f"✅ Ishchi muvaffaqiyatli qo‘shildi!\n\n👤 Ism: {name}\n📞 Tel: {phone}\n🆔 ID: {telegram_id}",
                        reply_markup=admin_kb)
    await state.clear()

# --- Mening ishchilarim ---
@dp.message(lambda m: m.text == "👥 Mening ishchilarim")
async def show_workers(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("❌ Bu bo‘lim faqat admin uchun.")
    workers = await get_workers()
    if not workers:
        return await message.reply("📭 Hozircha ishchi qo‘shilmagan.", reply_markup=admin_kb)
    text = "👥 Mening ishchilarim:\n\n"
    for w in workers:
        text += f"👤 {w[1]}\n📞 {w[2]}\n🆔 {w[3]}\n\n"
    await message.reply(text, reply_markup=admin_kb)

# --- Hisobot yuborish ---
@dp.message(lambda m: m.text == "🧾 Hisobot yuborish")
async def report_start(message: types.Message, state: FSMContext):
    worker = await check_worker(message.from_user.id)
    if not worker:
        return await message.reply("❌ Siz ro‘yxatda yo‘qsiz.")
    await state.set_state(ReportState.summa)
    await message.reply("💰 Sotuv summasini kiriting:", reply_markup=back_kb)

@dp.message(ReportState.summa)
async def report_summa(message: types.Message, state: FSMContext):
    await state.update_data(summa=message.text)
    await message.reply("⚖️ Nech kilo / nechta sotilganini kiriting:")
    await state.set_state(ReportState.quantity)

@dp.message(ReportState.quantity)
async def report_quantity(message: types.Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await message.reply("📝 Mahsulot nomi yoki tavsifini kiriting:")
    await state.set_state(ReportState.description)

@dp.message(ReportState.description)
async def report_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    summa = data["summa"]
    quantity = data["quantity"]
    description = message.text
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    await add_report(message.from_user.id, summa, quantity, description, now)
    worker = await check_worker(message.from_user.id)
    worker_name = worker[1] if worker else "Noma'lum"

    await message.reply(
        f"✅ Hisobot yuborildi!\n\n💰 {summa}\n⚖️ {quantity}\n📝 {description}\n⏰ {now}",
        reply_markup=worker_kb
    )

    await bot.send_message(
        ADMIN_ID,
        f"📩 Yangi hisobot keldi!\n\n👤 Ishchi: {worker_name}\n🆔 ID: {message.from_user.id}\n💰 {summa}\n⚖️ {quantity}\n📝 {description}\n⏰ {now}"
    )
    await state.clear()

# --- Bugungi hisobotlar ---
@dp.message(lambda m: m.text == "📊 Bugungi hisobotlar")
async def today_reports(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    reports = await get_todays_reports()
    if not reports:
        return await message.reply("📭 Bugungi hisobot hali ishchilar tomonidan yuborilmagan.",
                                   reply_markup=admin_kb)
    text = "📅 Bugungi hisobotlar:\n\n"
    for r in reports:
        worker = await check_worker(r[1])
        worker_name = worker[1] if worker else "Noma'lum"
        text += f"👤 {worker_name}\n💰 {r[2]}\n⚖️ {r[3]}\n📝 {r[4]}\n⏰ {r[5]}\n\n"
    await message.reply(text, reply_markup=admin_kb)

# --- Umumiy hisobotlar ---
@dp.message(lambda m: m.text == "📈 Umumiy hisobotlar")
async def all_reports(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    reports = await get_all_reports()
    if not reports:
        return await message.reply("📭 Hali hech qanday hisobot yuborilmagan.", reply_markup=admin_kb)
    text = "📊 Umumiy hisobotlar:\n\n"
    for r in reports:
        worker = await check_worker(r[1])
        worker_name = worker[1] if worker else "Noma'lum"
        text += f"👤 {worker_name}\n💰 {r[2]}\n⚖️ {r[3]}\n📝 {r[4]}\n⏰ {r[5]}\n\n"
    await message.reply(text, reply_markup=admin_kb)

# --- Ishchiga eslatma yuborish ---
@dp.message(lambda m: m.text == "📩 Ishchiga eslatma yuborish")
async def remind_workers(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    workers = await get_workers()
    if not workers:
        return await message.reply("❌ Hozircha ishchilar yo‘q.")
    for w in workers:
        try:
            await bot.send_message(w[3], "📨 Iltimos, bugungi hisobotni yuboring. Admin kutmoqda.")
        except:
            pass
    await message.reply("📨 Eslatma barcha ishchilarga yuborildi ✅", reply_markup=admin_kb)

# --- Botni ishga tushirish ---
async def main():
    await create_db()
    print("✅ Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
