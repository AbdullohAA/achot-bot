# Otchot Bot — Telegram hisobot bot (ready-to-deploy)

Bu loyiha — sotuvchilar hisobotlarini to'playdigan oddiy Telegram bot. 
Foydalanuvchilar (ishchilar) hisobot yuboradi, admin esa bugungi va umumiy otchotlarni ko'radi.

## Fayllar
- `main.py` — bot kodi
- `database.py` — SQLite yordamida ma'lumotlar bazasi
- `config.py` — token va admin ID konfiguratsiyasi (env orqali)
- `.env.example` — `.env` fayl namunasi (o'zgartiring)
- `requirements.txt` — kerakli paketlar
- `Procfile` — Render.com uchun (worker)
- `README.md` — bu hujjat

## Tez o'rnatish (lokal)
1. Papkani yuklab olib oching:
   ```bash
   unzip otchot_bot_full.zip -d otchot_bot_full
   cd otchot_bot_full
   ```
2. Virtual muhit yarating va aktivlashtiring:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   # yoki
   source venv/bin/activate  # Linux / macOS
   ```
3. Kutubxonalarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```
4. `.env` faylni `.env.example` dan nusxa qilib, o'zingizning `BOT_TOKEN` va `ADMIN_ID` ni qo'ying.
   ```bash
   copy .env.example .env   # Windows
   cp .env.example .env     # Linux/macOS
   ```
5. Botni ishga tushiring:
   ```bash
   python main.py
   ```
6. Telegramda botni topib `/start` yuboring.

## Deploy (Render.com)
1. GitHub repo yaratib fayllarni push qiling.
2. Render.com’da yangi **Web Service** yoki **Worker** yarating va GitHub repo bilan ulang.
3. Render’da Environment Variables bo'limiga `BOT_TOKEN` va `ADMIN_ID` qo'shing (qiymat sifatida token va raqam).
4. `Start Command` sifatida `python main.py` yozing.
5. Deploy qiling — bot ishga tushadi va 24/7 ishlaydi.

## Eslatma
- `.env` faylni GitHub ga push etmang — u maxfiy ma'lumotlarni o'z ichiga oladi.
- Agar admin bo'lmasangiz, admin komandalar ishlamaydi — `ADMIN_ID` to'g'ri ekanligini tekshiring.
