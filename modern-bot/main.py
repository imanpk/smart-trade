from fastapi import FastAPI, Request
from telegram_bot import send_signal_message, run_bot
import threading

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("📩 سیگنال دریافتی:", data)
        send_signal_message(data)
    except Exception as e:
        print("❌ خطا در پردازش:", e)

    return {"status": "ok"}

# اجرای ربات تلگرام
threading.Thread(target=run_bot).start()
