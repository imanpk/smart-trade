from fastapi import FastAPI, Request
from bot import send_signal_message

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("📩 سیگنال دریافتی:")
        print(data)
        send_signal_message(data)
    except Exception as e:
        print("❌ خطا در دریافت یا پردازش داده:", e)

    return {"status": "ok"}
