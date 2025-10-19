# Otchot Telegram Bot (Hisobot bot)

Bu loyiha — sotuvchilar hisobotlarini to'playdigan va adminga yuboradigan oddiy Telegram bot.
Fayllar:
- main.py — botning asosiy kodi
- config.py — bot token va admin ID
- database.py — SQLite bilan ishlash
- requirements.txt — kerakli pip paketlari

## O'rnatish
1. Python 3.8+ o'rnating.
2. Virtual muhit hosil qiling va aktivlashtiring:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate    # Windows
   ```
3. Talablarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
4. `config.py` faylini tahrir qiling: `BOT_TOKEN` va `ADMIN_ID` ni qo'ying.
5. Botni ishga tushiring:
   ```bash
   python main.py
   ```

## Foydalanish
- Admin (ADMIN_ID) menyuda: **Ishchi qo'shish**, **Bugungi achotlar**, **Umumiy achotlar**.
- Sotuvchi: **Sotuv qo'shish** tugmasi orqali hisobot yuboradi.
- Admin `/daily_report` komandasi bilan bugungi hisobotni olish mumkin (yoki botni cron bilan ishga tushiring)."# achot-bot" 
